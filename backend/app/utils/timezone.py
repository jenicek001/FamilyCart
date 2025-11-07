"""
Timezone utilities for the backend application.
Provides consistent UTC datetime handling across the application.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Return current UTC time as timezone-aware datetime.

    This should be used instead of datetime.utcnow() which returns naive datetime objects.
    Timezone-aware datetime objects ensure proper serialization with timezone information.

    Returns:
        datetime: Current UTC time with timezone information
    """
    return datetime.now(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime object to UTC timezone.

    Args:
        dt: datetime object (can be naive or timezone-aware)

    Returns:
        datetime: UTC datetime with timezone information
    """
    if dt.tzinfo is None:
        # Assume naive datetime is already in UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Convert timezone-aware datetime to UTC
        return dt.astimezone(timezone.utc)


def from_timestamp(timestamp: float) -> datetime:
    """
    Create timezone-aware UTC datetime from Unix timestamp.

    Args:
        timestamp: Unix timestamp (seconds since epoch)

    Returns:
        datetime: UTC datetime with timezone information
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
