"""ComponentChoices: component selection's structured output, consumed by cost estimation.

Each ComponentChoice is one priceable AWS resource in one region. Which fields a choice
must or may set depends on its service (see the tables below), so the Pricing API always
gets exactly the attributes it needs and nothing it would silently ignore.
"""

from collections import Counter
from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator

from schemas.requirements import AwsRegion

ServiceName = Literal["ec2", "rds", "elasticache", "s3", "data_transfer_out"]
# Exact values because the Pricing API filters on them (same reason system_type is a Literal).
EngineName = Literal["postgres", "mysql", "mariadb", "redis", "valkey", "memcached"]

# Per-service rules. id, service, region and citation are always allowed.
REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "ec2": ("instance_type",),
    "rds": ("instance_type", "engine"),
    "elasticache": ("instance_type", "engine"),
    "s3": ("storage_gb",),
    "data_transfer_out": ("monthly_gb",),
}
ALLOWED_FIELDS: dict[str, tuple[str, ...]] = {
    "ec2": ("instance_type", "count"),
    "rds": ("instance_type", "engine", "count", "storage_gb", "multi_az"),
    "elasticache": ("instance_type", "engine", "count"),
    "s3": ("storage_gb",),
    "data_transfer_out": ("monthly_gb",),
}
ENGINES_BY_SERVICE: dict[str, tuple[str, ...]] = {
    "rds": ("postgres", "mysql", "mariadb"),
    "elasticache": ("redis", "valkey", "memcached"),
}

# Service-specific fields and the value that means "not set".
_FIELD_DEFAULTS = {
    "instance_type": None,
    "engine": None,
    "count": 1,
    "storage_gb": None,
    "monthly_gb": None,
    "multi_az": False,
}


def _service_rule(service: str) -> str:
    rule = service + " (requires " + ", ".join(REQUIRED_FIELDS[service])
    optional = [f for f in ALLOWED_FIELDS[service] if f not in REQUIRED_FIELDS[service]]
    if optional:
        rule += "; optional " + ", ".join(optional)
    return rule + ")"


SERVICE_DESCRIPTION = (
    "AWS service to price. Fields per service: "
    + "; ".join(_service_rule(s) for s in get_args(ServiceName))
    + ". Leave every other field unset."
)


class ComponentChoice(BaseModel):
    """One priceable AWS resource in one region."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        min_length=1,
        description="Stable, unique key for this choice (e.g. 'db-primary-ap-south-1'); cost line items refer to it.",
    )
    service: ServiceName = Field(description=SERVICE_DESCRIPTION)
    region: AwsRegion = Field(
        description="AWS region code this resource runs in, e.g. ap-south-1."
    )
    instance_type: str | None = Field(
        default=None,
        description="Instance type exactly as AWS names it, e.g. m7i.large, db.r7g.large, cache.r7g.large.",
    )
    engine: EngineName | None = Field(
        default=None,
        description="Database or cache engine. rds: postgres, mysql or mariadb; elasticache: redis, valkey or memcached.",
    )
    count: int = Field(
        default=1, ge=1, description="Number of identical instances or nodes."
    )
    storage_gb: float | None = Field(
        default=None,
        gt=0,
        description="Provisioned storage in GB (s3 stored data, rds allocated storage).",
    )
    monthly_gb: float | None = Field(
        default=None,
        gt=0,
        description="Data transferred out to the internet per month, in GB.",
    )
    multi_az: bool = Field(
        default=False, description="rds only: true for a Multi-AZ deployment."
    )
    citation: str | None = Field(
        default=None,
        description="URL of the retrieved AWS documentation that supports this choice.",
    )

    @model_validator(mode="after")
    def _check_fields_for_service(self) -> "ComponentChoice":
        label = f"{self.service} component '{self.id}'"

        missing = [f for f in REQUIRED_FIELDS[self.service] if getattr(self, f) is None]
        if missing:
            raise ValueError(f"{label} is missing: {', '.join(missing)}")

        # A field counts as used when it differs from its default; explicit nulls are fine.
        unused = [
            f
            for f, default in _FIELD_DEFAULTS.items()
            if f not in ALLOWED_FIELDS[self.service] and getattr(self, f) != default
        ]
        if unused:
            raise ValueError(f"{label} does not use: {', '.join(unused)}")

        allowed_engines = ENGINES_BY_SERVICE.get(self.service)
        if allowed_engines and self.engine not in allowed_engines:
            raise ValueError(
                f"{label} engine '{self.engine}' is not valid; use one of: {', '.join(allowed_engines)}"
            )
        return self


class ComponentChoices(BaseModel):
    """Every AWS component chosen for the design, one entry per resource per region."""

    model_config = ConfigDict(extra="forbid")

    components: list[ComponentChoice] = Field(
        min_length=1,
        description="The chosen components. Multi-region designs list each component once per region.",
    )

    @model_validator(mode="after")
    def _check_unique_ids(self) -> "ComponentChoices":
        counts = Counter(c.id for c in self.components)
        duplicates = sorted(i for i, n in counts.items() if n > 1)
        if duplicates:
            raise ValueError(f"duplicate component ids: {', '.join(duplicates)}")
        return self
