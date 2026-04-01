from datetime import UTC, datetime


def get_current_time() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(UTC).isoformat()
