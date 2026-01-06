"""Prometheus metrics for monitoring."""
from prometheus_client import Counter, Gauge, Histogram, start_http_server, REGISTRY
from prometheus_client.core import CollectorRegistry

# ============================================
# Counters (monotonically increasing)
# ============================================

GIFTS_CHECKED = Counter(
    "gift_hunter_gifts_checked_total",
    "Total number of gifts checked",
)

GIFTS_PURCHASED = Counter(
    "gift_hunter_gifts_purchased_total",
    "Total number of gifts purchased",
    ["gift_name", "recipient"],
)

PURCHASES_FAILED = Counter(
    "gift_hunter_purchases_failed_total",
    "Total number of failed purchase attempts",
    ["reason"],
)

API_REQUESTS = Counter(
    "gift_hunter_api_requests_total",
    "Total Telegram API requests",
    ["method"],
)

# ============================================
# Gauges (can go up and down)
# ============================================

BALANCE = Gauge(
    "gift_hunter_balance_stars",
    "Current balance in Telegram Stars",
)

ACTIVE_MONITORING = Gauge(
    "gift_hunter_monitoring_active",
    "Whether the bot is actively monitoring (1=yes, 0=no)",
)

GIFTS_AVAILABLE = Gauge(
    "gift_hunter_gifts_available",
    "Number of gifts currently available for purchase",
)

# ============================================
# Histograms (distributions)
# ============================================

PURCHASE_DURATION = Histogram(
    "gift_hunter_purchase_duration_seconds",
    "Time taken to complete a purchase",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

CHECK_CYCLE_DURATION = Histogram(
    "gift_hunter_check_cycle_duration_seconds",
    "Time taken for a complete check cycle",
    buckets=[1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)


def start_metrics_server(port: int = 9090) -> None:
    """Start the Prometheus metrics HTTP server.
    
    Args:
        port: Port to expose metrics on (default: 9090)
    """
    start_http_server(port)


def reset_metrics() -> None:
    """Reset all metrics (useful for testing)."""
    # Note: This is a simplified version
    # In production, you might want more sophisticated reset logic
    ACTIVE_MONITORING.set(0)
    BALANCE.set(0)
    GIFTS_AVAILABLE.set(0)
