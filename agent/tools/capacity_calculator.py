from typing import Any

from .formula_library import FORMULA_LIBRARY
from llm.factory import get_small_llm

# Messaging / Chat Apps
def calc_peak_write_qps(dau, assumptions):
    msgs = assumptions.get("messages_per_user_per_day", 40)
    peak_factor = 4
    return {
        "name": "peak_write_qps",
        "formula": "DAU × msgs/user/day ÷ 86,400 × peak_factor",
        "value": dau * msgs / 86400 * peak_factor
    }

def calc_storage_growth_messages(dau, assumptions):
    msgs = assumptions.get("messages_per_user_per_day", 40)
    kb_per_msg = assumptions.get("avg_message_size_kb", 1)
    daily_storage_mb = dau * msgs * kb_per_msg / 1024
    monthly_storage_gb = daily_storage_mb * 30 / 1024
    return {
        "name": "storage_growth",
        "formula": "DAU × msgs/user/day × KB/msg",
        "daily_MB": daily_storage_mb,
        "monthly_GB": monthly_storage_gb
    }


# Social Networks
def calc_feed_updates_qps(dau, assumptions):
    posts = assumptions.get("posts_per_user_per_day", 5)
    peak_factor = 3
    return {
        "name": "feed_updates_qps",
        "formula": "DAU × posts/user/day ÷ 86,400 × peak_factor",
        "value": dau * posts / 86400 * peak_factor
    }

def calc_fanout_load(assumptions):
    posts = assumptions.get("posts_per_user_per_day", 5)
    followers = assumptions.get("avg_followers", 200)
    return {
        "name": "fanout_load",
        "formula": "posts × avg_followers",
        "value": posts * followers
    }


# Video Streaming
def calc_peak_concurrent_streams(dau, assumptions):
    avg_hours = assumptions.get("average_streaming_hours_per_user_per_day", 2)
    peak_factor = 4
    return {
        "name": "peak_concurrent_streams",
        "formula": "DAU × (avg_hours/24) × peak_factor",
        "value": dau * (avg_hours / 24) * peak_factor
    }

def calc_network_throughput(dau, assumptions):
    avg_hours = assumptions.get("average_streaming_hours_per_user_per_day", 2)
    peak_factor = 4
    mbps_per_stream = assumptions.get("mbps_per_stream", 3)
    concurrent = dau * (avg_hours / 24) * peak_factor
    return {
        "name": "network_throughput",
        "formula": "concurrent_streams × Mbps/stream",
        "value_Mbps": concurrent * mbps_per_stream
    }


# E-Commerce
def calc_orders_per_second(dau, assumptions):
    orders = assumptions.get("orders_per_user_per_day", 2)
    peak_factor = 3
    return {
        "name": "orders_per_second",
        "formula": "DAU × orders/user/day ÷ 86,400 × peak_factor",
        "value": dau * orders / 86400 * peak_factor
    }


# Ticket Booking
def calc_peak_booking_qps(dau, assumptions):
    bookings = assumptions.get("bookings_per_user_per_day", 1)
    peak_factor = 3
    return {
        "name": "peak_booking_qps",
        "formula": "DAU × bookings/user/day ÷ 86,400 × peak_factor",
        "value": dau * bookings / 86400 * peak_factor
    }


# Food Delivery
def calc_orders_per_second_delivery(dau, assumptions):
    orders = assumptions.get("orders_per_user_per_day", 2)
    peak_factor = 3
    return {
        "name": "orders_per_second",
        "formula": "DAU × orders/user/day ÷ 86,400 × peak_factor",
        "value": dau * orders / 86400 * peak_factor
    }

def calc_driver_concurrency(dau, assumptions):
    orders = assumptions.get("orders_per_user_per_day", 2)
    peak_factor = 3
    avg_delivery_time_min = assumptions.get("avg_delivery_time_minutes", 30)
    orders_sec = dau * orders / 86400 * peak_factor
    return {
        "name": "driver_concurrency",
        "formula": "orders/sec × avg_delivery_time",
        "value": orders_sec * avg_delivery_time_min
    }


# Ride-Hailing
def calc_rides_per_second(dau, assumptions):
    rides = assumptions.get("rides_per_user_per_day", 2)
    peak_factor = 3
    return {
        "name": "rides_per_second",
        "formula": "DAU × rides/user/day ÷ 86,400 × peak_factor",
        "value": dau * rides / 86400 * peak_factor
    }

def calc_driver_concurrency_rides(dau, assumptions):
    rides = assumptions.get("rides_per_user_per_day", 2)
    peak_factor = 3
    avg_trip_time_min = assumptions.get("avg_trip_time_minutes", 20)
    rides_sec = dau * rides / 86400 * peak_factor
    return {
        "name": "driver_concurrency",
        "formula": "rides/sec × avg_trip_time",
        "value": rides_sec * avg_trip_time_min
    }


# Analytics / Data Warehouse
def calc_query_throughput(dau, assumptions):
    queries = assumptions.get("queries_per_user_per_hour", 2)
    concurrent_users = dau * 0.1  # assume 10% are analysts
    return {
        "name": "query_throughput",
        "formula": "concurrent analysts × queries/hour ÷ 3600",
        "value": concurrent_users * queries / 3600
    }


# Banking / FinTech
def calc_transactions_per_second(dau, assumptions):
    txns = assumptions.get("transactions_per_user_per_day", 10)
    peak_factor = 3
    return {
        "name": "transactions_per_second",
        "formula": "DAU × txns/user/day ÷ 86,400 × peak_factor",
        "value": dau * txns / 86400 * peak_factor
    }


# Education / Learning
def calc_concurrent_students(dau, assumptions):
    avg_hours = assumptions.get("avg_learning_hours_per_user_per_day", 2)
    peak_factor = 3
    return {
        "name": "concurrent_students",
        "formula": "DAU × (avg_hours/24) × peak_factor",
        "value": dau * (avg_hours / 24) * peak_factor
    }


# Search Engines
def calc_search_qps(dau, assumptions):
    queries = assumptions.get("queries_per_user_per_day", 10)
    peak_factor = 3
    return {
        "name": "search_qps",
        "formula": "DAU × queries/user/day ÷ 86,400 × peak_factor",
        "value": dau * queries / 86400 * peak_factor
    }


# CDN
def calc_edge_requests_per_second(dau, assumptions):
    requests = assumptions.get("requests_per_user_per_day", 100)
    peak_factor = 3
    return {
        "name": "edge_requests_per_second",
        "formula": "DAU × requests/user/day ÷ 86,400 × peak_factor",
        "value": dau * requests / 86400 * peak_factor
    }

def normalize_assumptions(raw_assumptions):
    PARAMETER_MAP = {
        "messages_per_user_per_day": ["msgs_per_user", "daily_messages", "messages/day"],
        "queries_per_user_per_day": ["searches_per_user", "daily_queries", "queries/day"],
        "orders_per_user_per_day": ["purchases_per_user", "daily_orders", "orders/day"],
        "average_streaming_hours_per_user_per_day": ["streaming_hours", "watch_hours", "avg_streaming_time"]
    }

    normalized = {}
    for canonical, aliases in PARAMETER_MAP.items():
        for alias in aliases:
            if alias in raw_assumptions:
                normalized[canonical] = raw_assumptions[alias]
        if canonical not in normalized and canonical in raw_assumptions:
            normalized[canonical] = raw_assumptions[canonical]

    return normalized

def calculate_capacity(
    requirement_spec: dict[str, Any],
    thread_id: str = "abc",
) -> list[dict[str, Any]]:
    """Calculate workload metrics from a requirement specification."""
    system_type = map_system(requirement_spec.get("system_type", "").lower())
    dau = requirement_spec.get("explicit_requirements", {}).get("daily_active_users", 0)
    assumptions = normalize_assumptions(requirement_spec.get("assumptions", {}))
    results = []
    for category, formulas in FORMULA_LIBRARY.items():
        if category in system_type:
            for f in formulas:
                fun_name=globals()[f]
                calc = fun_name(dau, assumptions)
                print(f"Calculated {calc['name']} for {category}: {calc.get('value') or calc}")
                results.append({
                    "thread_id": thread_id,
                    "resource_category": calc["name"],
                    "requirement": calc.get("value") or calc
                })

    print("Capacity Calculation Results:")
    for result in results:
        print(f"  {result['resource_category']}: {result['requirement']}")
    return results

def map_system(req_system_type):
    small_llm = get_small_llm()
    # Build the prompt dynamically
    prompt = f"""
    You are a helper that maps system type from requirements spec to the system type in formula_library.
    
    System type from requirements spec:
    {req_system_type}
    
    formula library:
    {FORMULA_LIBRARY.items()}
    Task: Return the matching key from FORMULA_LIBRARY.

    """
    result = small_llm.invoke(prompt)
    text = result.content
    print(f"\nLLM raw response:\n{text}")
    return text