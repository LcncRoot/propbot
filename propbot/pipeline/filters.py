"""Filtering utilities for PropBot pipeline.

Implements freshness filtering (exclude expired opportunities)
and capability filtering (match NAICS codes and keywords).
"""

import json
import re
from datetime import datetime, date
from typing import Optional

from .normalizer import parse_iso_date


def is_expired(deadline_iso: Optional[str], reference_date: Optional[date] = None) -> bool:
    """
    Check if an opportunity has expired based on its deadline.

    Args:
        deadline_iso: Deadline in ISO 8601 format.
        reference_date: Date to compare against (defaults to today).

    Returns:
        True if expired (deadline has passed), False otherwise.
        Returns True if deadline is None (treat missing deadlines as expired).
    """
    if deadline_iso is None:
        return True  # Treat missing deadlines as expired

    ref_date = reference_date or date.today()

    deadline_dt = parse_iso_date(deadline_iso)
    if deadline_dt is None:
        return True  # Treat unparseable deadlines as expired

    return deadline_dt.date() < ref_date


def matches_capabilities(
    record: dict,
    naics_codes: set[str],
    keywords: set[str]
) -> tuple[bool, list[str], list[str]]:
    """
    Check if a record matches any capability filter.

    Matching logic:
    - For contracts: Check if NAICS code matches any in the filter set
    - For all: Check if any keyword appears in title or description

    Args:
        record: Opportunity record with 'naics_code', 'title', 'description' fields.
        naics_codes: Set of NAICS codes to match against.
        keywords: Set of keywords to search for (should be lowercase).

    Returns:
        Tuple of:
        - matches: True if any filter matched
        - matched_naics: List of matched NAICS codes
        - matched_keywords: List of matched keywords
    """
    matched_naics: list[str] = []
    matched_keywords: list[str] = []

    # Check NAICS code (primarily for contracts)
    naics = record.get("naics_code")
    if naics and naics in naics_codes:
        matched_naics.append(naics)

    # Build searchable text from title and description
    title = record.get("title") or ""
    description = record.get("description") or ""
    searchable_text = f"{title} {description}".lower()

    # Check keywords
    for keyword in keywords:
        # Use word boundary matching for short keywords to avoid false positives
        if len(keyword) <= 3:
            # For short keywords (aws, gcp, sre), require word boundaries
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, searchable_text):
                matched_keywords.append(keyword)
        else:
            # For longer keywords, simple substring match is fine
            if keyword in searchable_text:
                matched_keywords.append(keyword)

    matches = bool(matched_naics or matched_keywords)
    return matches, matched_naics, matched_keywords


def filter_freshness_only(
    record: dict,
    source: str,
    reference_date: Optional[date] = None
) -> tuple[Optional[dict], str]:
    """
    Apply only freshness filter to an opportunity record.

    Stores ALL opportunities regardless of capability match.
    Capability matching is done at search time via semantic search.

    Args:
        record: Raw opportunity record.
        source: Source name for the record.
        reference_date: Date to compare deadlines against.

    Returns:
        Tuple of:
        - Record (unchanged) or None if expired
        - Reason for filtering ('expired' or '')
    """
    from .normalizer import normalize_deadline

    raw_deadline = record.get("deadline")

    # Normalize deadline to ISO 8601 format before checking expiration
    deadline_iso = normalize_deadline(raw_deadline, source)

    # Check freshness
    if is_expired(deadline_iso, reference_date):
        return None, "expired"

    return record, ""


def filter_opportunity(
    record: dict,
    source: str,
    naics_codes: set[str],
    keywords: set[str],
    reference_date: Optional[date] = None
) -> tuple[Optional[dict], str]:
    """
    Apply all filters to an opportunity record.

    DEPRECATED: Use filter_freshness_only() instead.
    Capability filtering at ingest has been removed in favor of
    semantic search at query time.

    Filters applied:
    1. Freshness filter - reject if deadline has passed
    2. Capability filter - reject if no NAICS or keyword match

    Args:
        record: Raw opportunity record.
        source: Source name for the record.
        naics_codes: Set of NAICS codes to match against.
        keywords: Set of keywords to search for.
        reference_date: Date to compare deadlines against.

    Returns:
        Tuple of:
        - Filtered record with matched_keywords/matched_naics added, or None if filtered out
        - Reason for filtering ('passed', 'expired', 'no_capability_match', or '')
    """
    from .normalizer import normalize_deadline

    raw_deadline = record.get("deadline")

    # Normalize deadline to ISO 8601 format before checking expiration
    deadline_iso = normalize_deadline(raw_deadline, source)

    # Check freshness
    if is_expired(deadline_iso, reference_date):
        return None, "expired"

    # Check capability match
    matches, matched_naics, matched_keywords = matches_capabilities(
        record, naics_codes, keywords
    )

    if not matches:
        return None, "no_capability_match"

    # Enrich record with match info
    enriched_record = record.copy()
    enriched_record["matched_naics"] = json.dumps(matched_naics) if matched_naics else None
    enriched_record["matched_keywords"] = json.dumps(matched_keywords) if matched_keywords else None

    return enriched_record, ""
