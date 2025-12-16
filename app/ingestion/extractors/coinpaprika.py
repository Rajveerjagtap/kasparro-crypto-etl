"""CoinPaprika API extractor implementation."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.core.exceptions import APIException, ExtractionException
from app.core.logging import logger
from app.db.models import DataSource
from app.ingestion.base import BaseExtractor
from app.ingestion.transformers.schemas import CoinPaprikaResponse, RawCryptoRecord
from app.schemas.crypto import UnifiedCryptoDataCreate


class CoinPaprikaExtractor(BaseExtractor):
    """
    Extractor for CoinPaprika API.
    Handles rate limiting with exponential backoff.
    """

    BASE_URL = "https://api.coinpaprika.com/v1"
    RATE_LIMIT_DELAY = 1.0  # seconds between requests
    MAX_RETRIES = 3

    def __init__(self):
        self.source = DataSource.COINPAPRIKA
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            headers = {}
            if settings.coinpaprika_key:
                headers["Authorization"] = f"Bearer {settings.coinpaprika_key}"
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def _request_with_retry(self, endpoint: str) -> dict[str, Any]:
        """Execute request with exponential backoff on rate limit."""
        client = await self._get_client()

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.get(endpoint)

                if response.status_code == 429:
                    # Rate limited - exponential backoff
                    delay = self.RATE_LIMIT_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise APIException(
                    message=f"CoinPaprika API error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    details={"endpoint": endpoint},
                )
            except httpx.RequestError as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise APIException(
                        message=f"CoinPaprika request failed: {str(e)}",
                        details={"endpoint": endpoint},
                    )
                await asyncio.sleep(self.RATE_LIMIT_DELAY)

        raise APIException(message="Max retries exceeded for CoinPaprika API")

    async def fetch_data(
        self,
        last_processed: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch ticker data from CoinPaprika.
        Uses /tickers endpoint for bulk data.
        """
        try:
            # Fetch all tickers with quotes
            data = await self._request_with_retry("/tickers?quotes=USD")

            if not isinstance(data, list):
                raise ExtractionException(
                    message="Unexpected response format from CoinPaprika",
                    details={"type": type(data).__name__},
                )

            # Filter by last_processed if provided
            if last_processed:
                filtered = []
                for item in data:
                    last_updated = item.get("last_updated")
                    if last_updated:
                        try:
                            updated_dt = datetime.fromisoformat(
                                last_updated.replace("Z", "+00:00")
                            )
                            if updated_dt > last_processed:
                                filtered.append(item)
                        except (ValueError, TypeError):
                            filtered.append(item)
                    else:
                        filtered.append(item)
                data = filtered

            logger.info(f"CoinPaprika: fetched {len(data)} records")
            return data

        except APIException:
            raise
        except Exception as e:
            raise ExtractionException(
                message=f"Failed to fetch CoinPaprika data: {str(e)}",
            )
        finally:
            if self._client:
                await self._client.aclose()
                self._client = None

    def normalize(self, raw_data: list[dict[str, Any]]) -> list[UnifiedCryptoDataCreate]:
        """Transform CoinPaprika response to unified schema.

        Extracts source_id (CoinPaprika 'id') and name for canonical entity resolution.
        """
        normalized = []

        for item in raw_data:
            try:
                # Validate with CoinPaprika schema
                validated = CoinPaprikaResponse.model_validate(item)

                # Extract USD quote data
                usd_quote = validated.quotes.get("USD", {})

                # Build intermediate record for normalization
                record = RawCryptoRecord(
                    symbol=validated.symbol,
                    price_usd=usd_quote.get("price"),
                    market_cap=usd_quote.get("market_cap"),
                    volume_24h=usd_quote.get("volume_24h"),
                    timestamp=validated.last_updated or datetime.now(timezone.utc),
                )

                # Create unified schema with source metadata for entity resolution
                unified = UnifiedCryptoDataCreate(
                    symbol=record.symbol,
                    source_id=validated.id,  # CoinPaprika unique ID (e.g., "btc-bitcoin")
                    name=validated.name,  # Asset name (e.g., "Bitcoin")
                    price_usd=record.price_usd,
                    market_cap=record.market_cap,
                    volume_24h=record.volume_24h,
                    source=self.source,
                    timestamp=record.timestamp,
                )
                normalized.append(unified)

            except Exception as e:
                logger.warning(f"Failed to normalize CoinPaprika record: {e}")
                continue

        logger.info(f"CoinPaprika: normalized {len(normalized)} records")
        return normalized
