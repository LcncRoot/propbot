"""SAM.gov data source fetcher."""

import time
from datetime import datetime, timedelta
from typing import Iterator

import requests

from .base import BaseSource
from ..config import config


class SamGovSource(BaseSource):
    """Fetcher for SAM.gov contract opportunities via API."""

    def __init__(self, days_back: int = 90):
        """
        Initialize SAM.gov source.

        Args:
            days_back: Number of days back to fetch opportunities (default 90).
                       SAM.gov API limits date range queries.
        """
        self.days_back = days_back

    def get_source_name(self) -> str:
        return "sam.gov"

    def fetch(self) -> Iterator[dict]:
        """
        Fetch contract opportunities from SAM.gov API with pagination.

        Yields:
            Standardized opportunity dictionaries.
        """
        if not config.SAM_API_KEY:
            raise ValueError("SAM_API_KEY is not configured")

        # Calculate date range
        today = datetime.today()
        posted_from = (today - timedelta(days=self.days_back)).strftime("%m/%d/%Y")
        posted_to = today.strftime("%m/%d/%Y")

        offset = 0
        total_fetched = 0

        print(f"Fetching SAM.gov contracts from {posted_from} to {posted_to}")

        while True:
            params = {
                "api_key": config.SAM_API_KEY,
                "postedFrom": posted_from,
                "postedTo": posted_to,
                "limit": config.SAM_PAGE_SIZE,
                "offset": offset,
            }

            try:
                response = requests.get(
                    config.SAM_API_URL,
                    params=params,
                    timeout=60
                )
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error fetching SAM.gov contracts at offset {offset}: {e}")
                break

            data = response.json()
            contracts = data.get("opportunitiesData", [])

            if not contracts:
                print(f"No more contracts to fetch (total: {total_fetched})")
                break

            for contract in contracts:
                try:
                    yield self._normalize_contract(contract)
                except Exception as e:
                    notice_id = contract.get("noticeId", "unknown")
                    print(f"Error parsing contract {notice_id}: {e}")
                    continue

            total_fetched += len(contracts)
            print(f"Fetched {len(contracts)} contracts (total: {total_fetched})")

            offset += config.SAM_PAGE_SIZE

            # Rate limiting
            time.sleep(config.SAM_RATE_LIMIT_DELAY)

        print(f"Finished fetching SAM.gov contracts. Total: {total_fetched}")

    def _normalize_contract(self, contract: dict) -> dict:
        """
        Normalize SAM.gov API response to standard format.

        Args:
            contract: Raw contract data from SAM.gov API.

        Returns:
            Standardized opportunity dictionary.
        """
        notice_id = contract.get("noticeId", "")

        # Build SAM.gov URL
        url = f"https://sam.gov/opp/{notice_id}/view" if notice_id else None

        # Extract NAICS code (may be nested or a list)
        naics_code = None
        naics_data = contract.get("naicsCode")
        if naics_data:
            if isinstance(naics_data, list):
                naics_code = naics_data[0] if naics_data else None
            else:
                naics_code = str(naics_data)

        # Extract response deadline
        # SAM.gov uses "responseDeadLine" field with ISO 8601 format
        deadline = contract.get("responseDeadLine") or contract.get("archiveDate")

        return {
            "opportunity_id": notice_id,
            "title": contract.get("title", "").strip() if contract.get("title") else None,
            "description": contract.get("description", "").strip() if contract.get("description") else None,
            "agency": contract.get("department") or contract.get("fullParentPathName"),
            "deadline": deadline,  # ISO 8601 format typically
            "funding_amount": None,  # Contracts don't typically have this
            "naics_code": naics_code,
            "cfda_numbers": None,  # Contracts don't have CFDA numbers
            "url": url,
            "notice_type": contract.get("type"),  # e.g., "Sources Sought", "Solicitation", etc.
        }
