import logging
import re
from pathlib import Path

import pytest

from agent.tools import capacity_calculator as cc
from agent.tools.formula_library import ASSUMPTION_DEFAULTS

DAU = 1_000_000
SOURCE = Path(cc.__file__).read_text(encoding="utf-8")


# Expected values with empty assumptions, written out as the formula so they can be checked by hand.
DEFAULT_CASES = [
    (lambda: cc.calc_peak_write_qps(DAU, {})["value"], DAU * 40 / 86400 * 4),
    (lambda: cc.calc_storage_growth_messages(DAU, {})["daily_MB"], DAU * 40 * 1 / 1024),
    (
        lambda: cc.calc_storage_growth_messages(DAU, {})["monthly_GB"],
        DAU * 40 * 1 / 1024 * 30 / 1024,
    ),
    (lambda: cc.calc_feed_updates_qps(DAU, {})["value"], DAU * 5 / 86400 * 3),
    (lambda: cc.calc_fanout_load({})["value"], 5 * 200),
    (lambda: cc.calc_peak_concurrent_streams(DAU, {})["value"], DAU * (2 / 24) * 4),
    (lambda: cc.calc_network_throughput(DAU, {})["value_Mbps"], DAU * (2 / 24) * 4 * 3),
    (lambda: cc.calc_orders_per_second(DAU, {})["value"], DAU * 2 / 86400 * 3),
    (lambda: cc.calc_peak_booking_qps(DAU, {})["value"], DAU * 1 / 86400 * 3),
    (lambda: cc.calc_orders_per_second_delivery(DAU, {})["value"], DAU * 2 / 86400 * 3),
    (lambda: cc.calc_driver_concurrency(DAU, {})["value"], DAU * 2 / 86400 * 3 * 30),
    (lambda: cc.calc_rides_per_second(DAU, {})["value"], DAU * 2 / 86400 * 3),
    (
        lambda: cc.calc_driver_concurrency_rides(DAU, {})["value"],
        DAU * 2 / 86400 * 3 * 20,
    ),
    (lambda: cc.calc_query_throughput(DAU, {})["value"], DAU * 0.1 * 2 / 3600),
    (lambda: cc.calc_transactions_per_second(DAU, {})["value"], DAU * 10 / 86400 * 3),
    (lambda: cc.calc_concurrent_students(DAU, {})["value"], DAU * (2 / 24) * 3),
    (lambda: cc.calc_search_qps(DAU, {})["value"], DAU * 10 / 86400 * 3),
    (lambda: cc.calc_edge_requests_per_second(DAU, {})["value"], DAU * 100 / 86400 * 3),
]


@pytest.mark.parametrize(("compute", "expected"), DEFAULT_CASES)
def test_formulas_use_shared_defaults(compute, expected):
    assert compute() == pytest.approx(expected)


def test_peak_write_qps_matches_article():
    # 1M DAU × 40 msgs ÷ 86,400 × 4 ≈ 1,852 writes/sec
    assert cc.calc_peak_write_qps(DAU, {})["value"] == pytest.approx(1851.85, abs=0.01)


def test_passed_value_overrides_default():
    default = cc.calc_peak_write_qps(DAU, {})["value"]
    doubled = cc.calc_peak_write_qps(DAU, {"messages_per_user_per_day": 80})["value"]
    assert doubled == pytest.approx(default * 2)


def test_normalize_keeps_all_canonical_keys():
    raw = {key: default + 1 for key, default in ASSUMPTION_DEFAULTS.items()}
    assert cc.normalize_assumptions(raw) == raw


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [
        ("msgs_per_user", "messages_per_user_per_day"),
        ("searches_per_user", "queries_per_user_per_day"),
        ("daily_orders", "orders_per_user_per_day"),
        ("watch_hours", "average_streaming_hours_per_user_per_day"),
    ],
)
def test_normalize_still_maps_aliases(alias, canonical):
    assert cc.normalize_assumptions({alias: 7}) == {canonical: 7}


def test_normalize_canonical_key_wins_over_alias(caplog):
    with caplog.at_level(logging.WARNING):
        result = cc.normalize_assumptions(
            {"msgs_per_user": 60, "messages_per_user_per_day": 45}
        )
    assert result == {"messages_per_user_per_day": 45}
    assert "messages_per_user_per_day=45" in caplog.text
    assert "msgs_per_user=60" in caplog.text


def test_normalize_drops_unknown_keys_with_warning(caplog):
    with caplog.at_level(logging.WARNING):
        result = cc.normalize_assumptions({"msgs_per_day": 60, "avg_followers": 300})
    assert result == {"avg_followers": 300}
    assert "msgs_per_day" in caplog.text


def test_every_key_the_calculator_reads_is_in_assumption_defaults():
    read_keys = set(re.findall(r'_get\(assumptions, "([a-z_]+)"\)', SOURCE))
    assert read_keys == set(ASSUMPTION_DEFAULTS)


def test_no_hardcoded_defaults_left():
    # The only assumptions.get(...) allowed is the one inside _get.
    assert SOURCE.count("assumptions.get(") == 1
