"""Base class for data source fetchers."""

from abc import ABC, abstractmethod
from typing import Iterator


class BaseSource(ABC):
    """Abstract base class for opportunity data sources."""

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Return the canonical name of this data source.

        Returns:
            Source name (e.g., 'grants.gov', 'sam.gov').
        """
        pass

    @abstractmethod
    def fetch(self) -> Iterator[dict]:
        """
        Fetch opportunities from this source.

        Yields:
            Dictionary with standardized opportunity fields:
            - opportunity_id: Unique identifier
            - title: Opportunity title
            - description: Full description text
            - agency: Issuing agency name (optional)
            - deadline: Response deadline (raw format, will be normalized)
            - funding_amount: Funding amount in dollars (optional)
            - naics_code: NAICS code for contracts (optional)
            - cfda_numbers: CFDA numbers for grants (optional)
            - url: Link to opportunity details
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.get_source_name()}>"
