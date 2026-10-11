FORMULA_LIBRARY = {
    "messaging / chat apps": ["calc_peak_write_qps", "calc_storage_growth_messages"],
    "social networks": ["calc_feed_updates_qps", "calc_fanout_load"],
    "video streaming platforms": [
        "calc_peak_concurrent_streams",
        "calc_network_throughput",
    ],
    "e-commerce platforms": ["calc_orders_per_second"],
    "ticket booking systems": ["calc_peak_booking_qps"],
    "food delivery apps": [
        "calc_orders_per_second_delivery",
        "calc_driver_concurrency",
    ],
    "ride-hailing / mobility apps": [
        "calc_rides_per_second",
        "calc_driver_concurrency_rides",
    ],
    "analytics / data warehouse systems": ["calc_query_throughput"],
    "banking / fintech systems": ["calc_transactions_per_second"],
    "education / learning platforms": ["calc_concurrent_students"],
    "search engines / indexing systems": ["calc_search_qps"],
    "content delivery networks (cdn)": ["calc_edge_requests_per_second"],
}

# Every assumption key capacity_calculator.py reads, with its typical default.
# Single source of truth for the calculator, the RequirementSpec schema and the prompt.
ASSUMPTION_DEFAULTS = {
    # messaging / chat apps
    "messages_per_user_per_day": 40,
    "avg_message_size_kb": 1,
    # social networks
    "posts_per_user_per_day": 5,
    "avg_followers": 200,
    # video streaming platforms
    "average_streaming_hours_per_user_per_day": 2,
    "mbps_per_stream": 3,
    # e-commerce platforms, food delivery apps
    "orders_per_user_per_day": 2,
    # ticket booking systems
    "bookings_per_user_per_day": 1,
    # food delivery apps
    "avg_delivery_time_minutes": 30,
    # ride-hailing / mobility apps
    "rides_per_user_per_day": 2,
    "avg_trip_time_minutes": 20,
    # analytics / data warehouse systems
    "queries_per_user_per_hour": 2,
    # banking / fintech systems
    "transactions_per_user_per_day": 10,
    # education / learning platforms
    "avg_learning_hours_per_user_per_day": 2,
    # search engines / indexing systems
    "queries_per_user_per_day": 10,
    # content delivery networks (cdn)
    "requests_per_user_per_day": 100,
}
