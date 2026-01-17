"""Date normalization utilities for PropBot pipeline."""

from datetime import datetime
from typing import Optional

from dateutil import parser as dateparser
from dateutil.tz import UTC


def normalize_deadline(deadline_str: Optional[str], source: str) -> Optional[str]:
    """
    Normalize deadline string to ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

    Handles different date formats from various sources:
    - Grants.gov: MMDDYYYY (e.g., "09042024")
    - SAM.gov: ISO 8601 with timezone (e.g., "2025-03-05T17:00:00-05:00")

    Args:
        deadline_str: Raw deadline string from source.
        source: Source name ('grants.gov' or 'sam.gov').

    Returns:
        ISO 8601 formatted datetime string, or None if invalid/missing.
    """
    if not deadline_str or deadline_str in ("N/A", "n/a", ""):
        return None

    try:
        if source == "grants.gov":
            return _parse_grants_date(deadline_str)
        elif source == "sam.gov":
            return _parse_sam_date(deadline_str)
        else:
            # Attempt generic parsing
            return _parse_generic_date(deadline_str)
    except (ValueError, TypeError) as e:
        # Log but don't fail on bad dates
        print(f"Warning: Could not parse date '{deadline_str}' from {source}: {e}")
        return None


def _parse_grants_date(date_str: str) -> Optional[str]:
    """
    Parse Grants.gov date format (MMDDYYYY).

    Args:
        date_str: Date in MMDDYYYY format.

    Returns:
        ISO 8601 formatted string.
    """
    # Handle potential variations
    date_str = date_str.strip()

    # Expected format: MMDDYYYY (8 digits)
    if len(date_str) == 8 and date_str.isdigit():
        month = date_str[0:2]
        day = date_str[2:4]
        year = date_str[4:8]
        dt = datetime(int(year), int(month), int(day), 23, 59, 59)
        return dt.isoformat()

    # Try generic parsing as fallback
    return _parse_generic_date(date_str)


def _parse_sam_date(date_str: str) -> Optional[str]:
    """
    Parse SAM.gov date format (ISO 8601 with timezone).

    Args:
        date_str: Date in ISO 8601 format with timezone.

    Returns:
        ISO 8601 formatted string (UTC normalized).
    """
    date_str = date_str.strip()

    # Parse ISO 8601 with timezone awareness
    dt = dateparser.isoparse(date_str)

    # Convert to UTC if timezone-aware, then make naive for consistent storage
    if dt.tzinfo is not None:
        dt = dt.astimezone(UTC).replace(tzinfo=None)

    return dt.isoformat()


def _parse_generic_date(date_str: str) -> Optional[str]:
    """
    Attempt to parse date using dateutil's flexible parser.

    Args:
        date_str: Date string in unknown format.

    Returns:
        ISO 8601 formatted string.
    """
    dt = dateparser.parse(date_str)
    if dt is None:
        return None

    # If no time component, set to end of day
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        dt = dt.replace(hour=23, minute=59, second=59)

    return dt.isoformat()


def parse_iso_date(iso_str: Optional[str]) -> Optional[datetime]:
    """
    Parse an ISO 8601 date string back to datetime object.

    Args:
        iso_str: ISO 8601 formatted date string.

    Returns:
        datetime object or None.
    """
    if not iso_str:
        return None

    try:
        return datetime.fromisoformat(iso_str)
    except ValueError:
        return None
