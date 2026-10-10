from agent.tools.formula_library import ASSUMPTION_DEFAULTS, FORMULA_LIBRARY
from observability.logger import get_logger

logger = get_logger(__name__)


def _get(assumptions: dict, key: str) -> float:
    return assumptions.get(key, ASSUMPTION_DEFAULTS[key])


# Messaging / Chat Apps
def calc_peak_write_qps(dau, assumptions):
    msgs = _get(assumptions, "messages_per_user_per_day")
    peak_factor = 4
    return {
        "name": "peak_write_qps",
        "formula": "DAU × msgs/user/day ÷ 86,400 × peak_factor",
        "value": dau * msgs / 86400 * peak_factor,
    }


def calc_storage_growth_messages(dau, assumptions):
    msgs = _get(assumptions, "messages_per_user_per_day")
    kb_per_msg = _get(assumptions, "avg_message_size_kb")
    daily_storage_mb = dau * msgs * kb_per_msg / 1024
    monthly_storage_gb = daily_storage_mb * 30 / 1024
    return {
        "name": "storage_growth",
        "formula": "DAU × msgs/user/day × KB/msg",
        "daily_MB": daily_storage_mb,
        "monthly_GB": monthly_storage_gb,
    }


# Social Networks
def calc_feed_updates_qps(dau, assumptions):
    posts = _get(assumptions, "posts_per_user_per_day")
    peak_factor = 3
    return {
        "name": "feed_updates_qps",
        "formula": "DAU × posts/user/day ÷ 86,400 × peak_factor",
        "value": dau * posts / 86400 * peak_factor,
    }


def calc_fanout_load(assumptions):
    posts = _get(assumptions, "posts_per_user_per_day")
    followers = _get(assumptions, "avg_followers")
    return {
        "name": "fanout_load",
        "formula": "posts × avg_followers",
        "value": posts * followers,
    }


# Video Streaming
def calc_peak_concurrent_streams(dau, assumptions):
    avg_hours = _get(assumptions, "average_streaming_hours_per_user_per_day")
    peak_factor = 4
    return {
        "name": "peak_concurrent_streams",
        "formula": "DAU × (avg_hours/24) × peak_factor",
        "value": dau * (avg_hours / 24) * peak_factor,
    }


def calc_network_throughput(dau, assumptions):
    avg_hours = _get(assumptions, "average_streaming_hours_per_user_per_day")
    peak_factor = 4
    mbps_per_stream = _get(assumptions, "mbps_per_stream")
    concurrent = dau * (avg_hours / 24) * peak_factor
    return {
        "name": "network_throughput",
        "formula": "concurrent_streams × Mbps/stream",
        "value_Mbps": concurrent * mbps_per_stream,
    }


# E-Commerce
def calc_orders_per_second(dau, assumptions):
    orders = _get(assumptions, "orders_per_user_per_day")
    peak_factor = 3
    return {
        "name": "orders_per_second",
        "formula": "DAU × orders/user/day ÷ 86,400 × peak_factor",
        "value": dau * orders / 86400 * peak_factor,
    }


# Ticket Booking
def calc_peak_booking_qps(dau, assumptions):
    bookings = _get(assumptions, "bookings_per_user_per_day")
    peak_factor = 3
    return {
        "name": "peak_booking_qps",
        "formula": "DAU × bookings/user/day ÷ 86,400 × peak_factor",
        "value": dau * bookings / 86400 * peak_factor,
    }


# Food Delivery
def calc_orders_per_second_delivery(dau, assumptions):
    orders = _get(assumptions, "orders_per_user_per_day")
    peak_factor = 3
    return {
        "name": "orders_per_second",
        "formula": "DAU × orders/user/day ÷ 86,400 × peak_factor",
        "value": dau * orders / 86400 * peak_factor,
    }


def calc_driver_concurrency(dau, assumptions):
    orders = _get(assumptions, "orders_per_user_per_day")
    peak_factor = 3
    avg_delivery_time_min = _get(assumptions, "avg_delivery_time_minutes")
    orders_sec = dau * orders / 86400 * peak_factor
    return {
        "name": "driver_concurrency",
        "formula": "orders/sec × avg_delivery_time",
        "value": orders_sec * avg_delivery_time_min,
    }


# Ride-Hailing
def calc_rides_per_second(dau, assumptions):
    rides = _get(assumptions, "rides_per_user_per_day")
    peak_factor = 3
    return {
        "name": "rides_per_second",
        "formula": "DAU × rides/user/day ÷ 86,400 × peak_factor",
        "value": dau * rides / 86400 * peak_factor,
    }


def calc_driver_concurrency_rides(dau, assumptions):
    rides = _get(assumptions, "rides_per_user_per_day")
    peak_factor = 3
    avg_trip_time_min = _get(assumptions, "avg_trip_time_minutes")
    rides_sec = dau * rides / 86400 * peak_factor
    return {
        "name": "driver_concurrency",
        "formula": "rides/sec × avg_trip_time",
        "value": rides_sec * avg_trip_time_min,
    }


# Analytics / Data Warehouse
def calc_query_throughput(dau, assumptions):
    queries = _get(assumptions, "queries_per_user_per_hour")
    concurrent_users = dau * 0.1  # assume 10% are analysts
    return {
        "name": "query_throughput",
        "formula": "concurrent analysts × queries/hour ÷ 3600",
        "value": concurrent_users * queries / 3600,
    }


# Banking / FinTech
def calc_transactions_per_second(dau, assumptions):
    txns = _get(assumptions, "transactions_per_user_per_day")
    peak_factor = 3
    return {
        "name": "transactions_per_second",
        "formula": "DAU × txns/user/day ÷ 86,400 × peak_factor",
        "value": dau * txns / 86400 * peak_factor,
    }


# Education / Learning
def calc_concurrent_students(dau, assumptions):
    avg_hours = _get(assumptions, "avg_learning_hours_per_user_per_day")
    peak_factor = 3
    return {
        "name": "concurrent_students",
        "formula": "DAU × (avg_hours/24) × peak_factor",
        "value": dau * (avg_hours / 24) * peak_factor,
    }


# Search Engines
def calc_search_qps(dau, assumptions):
    queries = _get(assumptions, "queries_per_user_per_day")
    peak_factor = 3
    return {
        "name": "search_qps",
        "formula": "DAU × queries/user/day ÷ 86,400 × peak_factor",
        "value": dau * queries / 86400 * peak_factor,
    }


# CDN
def calc_edge_requests_per_second(dau, assumptions):
    requests = _get(assumptions, "requests_per_user_per_day")
    peak_factor = 3
    return {
        "name": "edge_requests_per_second",
        "formula": "DAU × requests/user/day ÷ 86,400 × peak_factor",
        "value": dau * requests / 86400 * peak_factor,
    }


def normalize_assumptions(raw_assumptions):
    PARAMETER_MAP = {
        "messages_per_user_per_day": [
            "msgs_per_user",
            "daily_messages",
            "messages/day",
        ],
        "queries_per_user_per_day": [
            "searches_per_user",
            "daily_queries",
            "queries/day",
        ],
        "orders_per_user_per_day": ["purchases_per_user", "daily_orders", "orders/day"],
        "average_streaming_hours_per_user_per_day": [
            "streaming_hours",
            "watch_hours",
            "avg_streaming_time",
        ],
    }

    normalized = {}
    for canonical, aliases in PARAMETER_MAP.items():
        for alias in aliases:
            if alias not in raw_assumptions:
                continue
            if canonical in raw_assumptions:
                logger.warning(
                    f"Both {canonical}={raw_assumptions[canonical]} and alias "
                    f"{alias}={raw_assumptions[alias]} given; using {canonical}"
                )
            else:
                normalized[canonical] = raw_assumptions[alias]
        if canonical not in normalized and canonical in raw_assumptions:
            normalized[canonical] = raw_assumptions[canonical]

    # Pass through every other canonical key the formulas read; drop the rest loudly.
    for key, value in raw_assumptions.items():
        if key in ASSUMPTION_DEFAULTS and key not in normalized:
            normalized[key] = value

    known_aliases = {alias for aliases in PARAMETER_MAP.values() for alias in aliases}
    unknown = set(raw_assumptions) - set(ASSUMPTION_DEFAULTS) - known_aliases
    if unknown:
        logger.warning(f"Dropping unknown assumptions: {sorted(unknown)}")

    return normalized


def capacity_calculator(requirement_spec, thread_id="abc"):
    system_type = requirement_spec.get("system_type", "").lower()
    dau = requirement_spec.get("explicit_requirements", {}).get("daily_active_users", 0)
    assumptions = normalize_assumptions(requirement_spec.get("assumptions", {}))
    results = []
    for category, formulas in FORMULA_LIBRARY.items():
        if category in system_type:
            for f in formulas:
                calc = f(dau, assumptions)
                results.append(
                    {
                        "thread_id": thread_id,
                        "resource_category": calc["name"],
                        "requirement": calc.get("value") or calc,
                    }
                )

    print("Capacity Calculation Results:")
    for result in results:
        print(f"  {result['resource_category']}: {result['requirement']}")
    return results
