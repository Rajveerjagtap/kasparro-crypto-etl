"""CoinGecko API extractor implementation."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.core.exceptions import APIException, ExtractionException
from app.core.logging import logger
from app.db.models import DataSource
from app.ingestion.base import BaseExtractor
from app.ingestion.transformers.schemas import CoinGeckoResponse, RawCryptoRecord
from app.schemas.crypto import UnifiedCryptoDataCreate


class CoinGeckoExtractor(BaseExtractor):
    """
    Extractor for CoinGecko API.
    Free tier: 10-30 calls/min depending on endpoint.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"
    PRO_BASE_URL = "https://pro-api.coingecko.com/api/v3"
    RATE_LIMIT_DELAY = 2.0  # seconds between requests (conservative for free tier)
    MAX_RETRIES = 3
    PAGE_SIZE = 250  # max per_page for markets endpoint

    def __init__(self):
        self.source = DataSource.COINGECKO
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            # Use pro API if key provided
            base_url = self.PRO_BASE_URL if settings.coingecko_key else self.BASE_URL
            headers = {}
            if settings.coingecko_key:
                headers["x-cg-pro-api-key"] = settings.coingecko_key

            self._client = httpx.AsyncClient(
                base_url=base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def _request_with_retry(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Execute request with exponential backoff on rate limit."""
        client = await self._get_client()

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.get(endpoint, params=params)

                if response.status_code == 429:
                    delay = self.RATE_LIMIT_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise APIException(
                    message=f"CoinGecko API error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    details={"endpoint": endpoint},
                )
            except httpx.RequestError as e:
                if attempt == self.MAX_RETRIES - 1:
                    raise APIException(
                        message=f"CoinGecko request failed: {str(e)}",
                        details={"endpoint": endpoint},
                    )
                await asyncio.sleep(self.RATE_LIMIT_DELAY)

        raise APIException(message="Max retries exceeded for CoinGecko API")

    async def fetch_data(
        self,
        last_processed: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch market data from CoinGecko.
        Uses /coins/markets endpoint for comprehensive data.
        """
        try:
            all_data: list[dict[str, Any]] = []
            page = 1

            # Fetch paginated results
            while True:
                params = {
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": self.PAGE_SIZE,
                    "page": page,
                    "sparkline": "false",
                }

                data = await self._request_with_retry("/coins/markets", params)

                if not data:
                    break

                all_data.extend(data)

                # Limit to first 2 pages (500 coins) to avoid rate limits
                if page >= 2 or len(data) < self.PAGE_SIZE:
                    break

                page += 1
                await asyncio.sleep(self.RATE_LIMIT_DELAY)

            # Filter by last_processed if provided
            if last_processed:
                filtered = []
                for item in all_data:
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
                all_data = filtered

            logger.info(f"CoinGecko: fetched {len(all_data)} records")
            return all_data

        except APIException:
            raise
        except Exception as e:
            raise ExtractionException(
                message=f"Failed to fetch CoinGecko data: {str(e)}",
            )
        finally:
            if self._client:
                await self._client.aclose()
                self._client = None

    def normalize(self, raw_data: list[dict[str, Any]]) -> list[UnifiedCryptoDataCreate]:
        """Transform CoinGecko response to unified schema."""
        normalized = []

        for item in raw_data:
            try:
                # Validate with CoinGecko schema
                validated = CoinGeckoResponse.model_validate(item)

                # Build intermediate record
                record = RawCryptoRecord(
                    symbol=validated.symbol,
                    price_usd=validated.current_price,
                    market_cap=validated.market_cap,
                    volume_24h=validated.total_volume,
                    timestamp=validated.last_updated or datetime.now(timezone.utc),
                )

                # Create unified schema
                unified = UnifiedCryptoDataCreate(
                    symbol=record.symbol,
                    price_usd=record.price_usd,
                    market_cap=record.market_cap,
                    volume_24h=record.volume_24h,
                    source=self.source,
                    timestamp=record.timestamp,
                )
                normalized.append(unified)

            except Exception as e:
                logger.warning(f"Failed to normalize CoinGecko record: {e}")
                continue

        logger.info(f"CoinGecko: normalized {len(normalized)} records")
        return normalized
