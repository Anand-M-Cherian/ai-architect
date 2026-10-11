import copy
from typing import get_args

import pytest
from pydantic import ValidationError

from schemas import ComponentChoices, EngineName, ServiceName
from schemas.components import ALLOWED_FIELDS, ENGINES_BY_SERVICE, REQUIRED_FIELDS

DOCS = "https://docs.aws.amazon.com"


def region_components(region):
    return [
        {
            "id": f"app-{region}",
            "service": "ec2",
            "region": region,
            "instance_type": "m7i.large",
            "count": 6,
            "citation": f"{DOCS}/ec2/latest/instancetypes/gp.html",
        },
        {
            "id": f"db-{region}",
            "service": "rds",
            "region": region,
            "instance_type": "db.r7g.large",
            "engine": "postgres",
            "storage_gb": 500,
            "multi_az": True,
            "citation": f"{DOCS}/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html",
        },
        {
            "id": f"cache-{region}",
            "service": "elasticache",
            "region": region,
            "instance_type": "cache.r7g.large",
            "engine": "valkey",
            "count": 2,
            "citation": f"{DOCS}/AmazonElastiCache/latest/dg/WhatIs.html",
        },
        {
            "id": f"media-{region}",
            "service": "s3",
            "region": region,
            "storage_gb": 2000,
            "citation": f"{DOCS}/AmazonS3/latest/userguide/Welcome.html",
        },
        {
            "id": f"egress-{region}",
            "service": "data_transfer_out",
            "region": region,
            "monthly_gb": 5000,
            "citation": f"{DOCS}/cur/latest/userguide/cur-data-transfers-charges.html",
        },
    ]


WHATSAPP = {
    "components": region_components("ap-south-1") + region_components("us-east-1")
}

# One minimal valid component per service, used as the base for single-rule tests.
MINIMAL = {
    "ec2": {"instance_type": "m7i.large"},
    "rds": {"instance_type": "db.r7g.large", "engine": "postgres"},
    "elasticache": {"instance_type": "cache.r7g.large", "engine": "redis"},
    "s3": {"storage_gb": 100},
    "data_transfer_out": {"monthly_gb": 100},
}


def one(service, **changes):
    component = {"id": f"{service}-1", "service": service, "region": "ap-south-1"}
    component.update(MINIMAL[service])
    component.update(changes)
    return {"components": [component]}


def error_text(data):
    with pytest.raises(ValidationError) as exc:
        ComponentChoices.model_validate(data)
    return str(exc.value)


def test_valid_whatsapp_choices_parse():
    choices = ComponentChoices.model_validate(WHATSAPP)
    assert len(choices.components) == 10
    assert {c.region for c in choices.components} == {"ap-south-1", "us-east-1"}


@pytest.mark.parametrize("service", list(MINIMAL))
def test_minimal_component_per_service_parses(service):
    ComponentChoices.model_validate(one(service))


def test_defaults():
    component = ComponentChoices.model_validate(one("ec2")).components[0]
    assert component.count == 1
    assert component.multi_az is False
    assert component.citation is None


@pytest.mark.parametrize(
    ("service", "field"),
    [(s, f) for s, fields in REQUIRED_FIELDS.items() for f in fields],
)
def test_missing_required_field_rejected(service, field):
    data = one(service)
    del data["components"][0][field]
    text = error_text(data)
    assert f"{service} component '{service}-1' is missing: {field}" in text


@pytest.mark.parametrize(
    ("service", "field", "value"),
    [
        ("s3", "instance_type", "m7i.large"),
        ("ec2", "engine", "postgres"),
        ("elasticache", "multi_az", True),
        ("ec2", "storage_gb", 50),
        ("s3", "count", 3),
        ("data_transfer_out", "storage_gb", 10),
    ],
)
def test_field_not_used_by_service_rejected(service, field, value):
    text = error_text(one(service, **{field: value}))
    assert f"{service} component '{service}-1' does not use: {field}" in text


def test_explicit_nulls_on_unused_fields_accepted():
    data = one("s3", instance_type=None, engine=None, monthly_gb=None, citation=None)
    ComponentChoices.model_validate(data)


def test_rds_accepts_storage_and_multi_az():
    component = ComponentChoices.model_validate(
        one("rds", storage_gb=200, multi_az=True)
    ).components[0]
    assert component.storage_gb == 200
    assert component.multi_az is True


@pytest.mark.parametrize(
    ("service", "engine"), [("rds", "redis"), ("elasticache", "postgres")]
)
def test_engine_service_mismatch_rejected_with_valid_engines(service, engine):
    text = error_text(one(service, engine=engine))
    assert f"engine '{engine}' is not valid" in text
    assert ", ".join(ENGINES_BY_SERVICE[service]) in text


def test_unknown_engine_rejected():
    error_text(one("rds", engine="oracle"))


def test_unknown_service_rejected():
    data = one("ec2")
    data["components"][0]["service"] = "lambda"
    error_text(data)


def test_bad_region_rejected_with_examples():
    assert "ap-south-1" in error_text(one("ec2", region="Mumbai"))


def test_zero_count_rejected():
    error_text(one("ec2", count=0))


@pytest.mark.parametrize("storage_gb", [0, -10])
def test_non_positive_storage_rejected(storage_gb):
    error_text(one("s3", storage_gb=storage_gb))


def test_extra_top_level_key_rejected():
    data = copy.deepcopy(WHATSAPP)
    data["total_cost"] = 100
    error_text(data)


def test_extra_component_key_rejected():
    error_text(one("ec2", vcpus=2))


def test_duplicate_ids_rejected_and_named():
    data = copy.deepcopy(WHATSAPP)
    data["components"][1]["id"] = data["components"][0]["id"]
    assert "duplicate component ids: app-ap-south-1" in error_text(data)


def test_empty_component_list_rejected():
    error_text({"components": []})


def test_json_round_trip():
    choices = ComponentChoices.model_validate(WHATSAPP)
    again = ComponentChoices.model_validate(choices.model_dump(mode="json"))
    assert again == choices


def test_rule_tables_cover_every_service_and_engine():
    services = set(get_args(ServiceName))
    assert set(REQUIRED_FIELDS) == services
    assert set(ALLOWED_FIELDS) == services
    for service in services:
        assert set(REQUIRED_FIELDS[service]) <= set(ALLOWED_FIELDS[service])
    engines = {e for es in ENGINES_BY_SERVICE.values() for e in es}
    assert engines == set(get_args(EngineName))
    assert all("engine" in REQUIRED_FIELDS[s] for s in ENGINES_BY_SERVICE)


def test_service_description_states_rules_per_service():
    schema = ComponentChoices.model_json_schema()
    description = schema["$defs"]["ComponentChoice"]["properties"]["service"][
        "description"
    ]
    assert "ec2 (requires instance_type; optional count)" in description
    assert (
        "rds (requires instance_type, engine; optional count, storage_gb, multi_az)"
        in description
    )
    assert "s3 (requires storage_gb)" in description
