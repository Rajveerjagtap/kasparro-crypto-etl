"""Abstract base class for all data extractors."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from app.schemas.crypto import UnifiedCryptoDataCreate


class BaseExtractor(ABC):
    """
    Abstract base class defining the contract for all data extractors.
    Each extractor must implement fetch_data() and normalize() methods.
    """

    @abstractmethod
    async def fetch_data(
        self,
        last_processed: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch raw data from the source.

        Args:
            last_processed: Timestamp of last successful fetch for incremental loading.

        Returns:
            List of raw data dictionaries.
        """
        pass

    @abstractmethod
    def normalize(self, raw_data: list[dict[str, Any]]) -> list[UnifiedCryptoDataCreate]:
        """
        Transform raw data into unified schema.

        Args:
            raw_data: List of raw data dictionaries from fetch_data().

        Returns:
            List of normalized UnifiedCryptoDataCreate objects.
        """
        pass

    async def extract(
        self,
        last_processed: Optional[datetime] = None,
    ) -> tuple[list[dict[str, Any]], list[UnifiedCryptoDataCreate]]:
        """
        Execute full extraction pipeline: fetch and normalize.

        Returns:
            Tuple of (raw_data, normalized_data).
        """
        raw_data = await self.fetch_data(last_processed)
        normalized = self.normalize(raw_data)
        return raw_data, normalized
