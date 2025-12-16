"""
Asset Resolution Service - Maps source-specific identifiers to canonical Coin entities.

This service is the core of proper data normalization:
1. Resolves source IDs to canonical Coin entities
2. Creates new Coins when encountering unknown assets
3. Maintains source-to-canonical mappings
4. Handles symbol disambiguation across sources

Architecture:
    Source Data → AssetResolver → coin_id → UnifiedCryptoData
                       ↓
                 Coin (master)
                       ↓
              SourceAssetMapping
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.models import Coin, DataSource, SourceAssetMapping


class AssetResolver:
    """
    Resolves source-specific asset identifiers to canonical Coin entities.

    The resolver maintains a cache of mappings and creates new entities
    when encountering assets not yet in the system.

    Usage:
        resolver = AssetResolver()
        coin_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
            source_name="Bitcoin",
        )
    """

    def __init__(self):
        # In-memory cache: (source, source_id) -> coin_id
        self._mapping_cache: dict[tuple[DataSource, str], int] = {}
        # Symbol to coin_id cache for fallback resolution
        self._symbol_cache: dict[str, int] = {}
        # Track if cache has been preloaded
        self._cache_loaded: bool = False

    async def resolve_asset(
        self,
        session: AsyncSession,
        source: DataSource,
        source_id: str,
        source_symbol: str,
        source_name: Optional[str] = None,
    ) -> int:
        """
        Resolve a source-specific asset to its canonical Coin ID.

        Resolution order:
        1. Check cache for exact (source, source_id) match
        2. Query source_asset_mappings for existing mapping
        3. Query coins by symbol for potential match
        4. Create new Coin and mapping if not found

        Args:
            session: Database session
            source: Data source (COINGECKO, COINPAPRIKA, CSV)
            source_id: Source-specific identifier (e.g., "bitcoin" for CoinGecko)
            source_symbol: Symbol as provided by source (e.g., "btc")
            source_name: Optional asset name from source

        Returns:
            Canonical coin_id for the asset
        """
        cache_key = (source, source_id)

        # 1. Check in-memory cache
        if cache_key in self._mapping_cache:
            return self._mapping_cache[cache_key]

        # Normalize symbol to uppercase
        normalized_symbol = source_symbol.upper().strip()

        # 2. Query existing mapping
        mapping_query = select(SourceAssetMapping).where(
            SourceAssetMapping.source == source,
            SourceAssetMapping.source_id == source_id,
        )
        mapping_result = await session.execute(mapping_query)
        existing_mapping = mapping_result.scalar_one_or_none()

        if existing_mapping:
            self._mapping_cache[cache_key] = existing_mapping.coin_id
            self._symbol_cache[normalized_symbol] = existing_mapping.coin_id
            return existing_mapping.coin_id

        # 3. Try to find existing Coin by symbol (for cross-source matching)
        coin_query = select(Coin).where(Coin.symbol == normalized_symbol)
        coin_result = await session.execute(coin_query)
        existing_coin = coin_result.scalar_one_or_none()

        if existing_coin:
            # Create new mapping for this source to existing coin
            await self._create_mapping(
                session,
                coin_id=existing_coin.id,
                source=source,
                source_id=source_id,
                source_symbol=source_symbol,
                source_name=source_name,
            )
            self._mapping_cache[cache_key] = existing_coin.id
            self._symbol_cache[normalized_symbol] = existing_coin.id
            logger.info(
                f"Linked {source.value}:{source_id} to existing Coin {existing_coin.symbol} (id={existing_coin.id})"
            )
            return existing_coin.id

        # 4. Create new Coin and mapping (asset not yet in system)
        coin_id = await self._create_coin_with_mapping(
            session,
            symbol=normalized_symbol,
            name=source_name or normalized_symbol,
            source=source,
            source_id=source_id,
            source_symbol=source_symbol,
        )

        self._mapping_cache[cache_key] = coin_id
        self._symbol_cache[normalized_symbol] = coin_id
        return coin_id

    async def resolve_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        source: DataSource,
    ) -> int:
        """
        Resolve a coin by symbol only (fallback for sources without unique IDs).

        Used primarily for CSV imports where we only have symbols.

        Args:
            session: Database session
            symbol: Asset symbol (e.g., "BTC")
            source: Data source

        Returns:
            Canonical coin_id
        """
        normalized_symbol = symbol.upper().strip()

        # Check symbol cache
        if normalized_symbol in self._symbol_cache:
            return self._symbol_cache[normalized_symbol]

        # Query existing coin by symbol
        query = select(Coin).where(Coin.symbol == normalized_symbol)
        result = await session.execute(query)
        coin = result.scalar_one_or_none()

        if coin:
            self._symbol_cache[normalized_symbol] = coin.id

            # Ensure mapping exists for this source
            await self._ensure_mapping_exists(
                session,
                coin_id=coin.id,
                source=source,
                source_id=normalized_symbol,
                source_symbol=normalized_symbol,
            )

            return coin.id

        # Create new coin for unknown symbol
        coin_id = await self._create_coin_with_mapping(
            session,
            symbol=normalized_symbol,
            name=normalized_symbol,
            source=source,
            source_id=normalized_symbol,
            source_symbol=normalized_symbol,
        )

        self._symbol_cache[normalized_symbol] = coin_id
        return coin_id

    async def get_coin_id_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
    ) -> Optional[int]:
        """
        Get coin_id by symbol without creating new entries.

        Returns:
            coin_id if found, None otherwise
        """
        normalized_symbol = symbol.upper().strip()

        if normalized_symbol in self._symbol_cache:
            return self._symbol_cache[normalized_symbol]

        query = select(Coin.id).where(Coin.symbol == normalized_symbol)
        result = await session.execute(query)
        coin_id = result.scalar_one_or_none()

        if coin_id:
            self._symbol_cache[normalized_symbol] = coin_id

        return coin_id

    async def _create_coin_with_mapping(
        self,
        session: AsyncSession,
        symbol: str,
        name: str,
        source: DataSource,
        source_id: str,
        source_symbol: str,
    ) -> int:
        """Create a new Coin entity and its source mapping."""
        # Generate unique slug
        slug = self._generate_slug(symbol, name)

        # Create new Coin
        coin = Coin(
            symbol=symbol,
            name=name,
            slug=slug,
        )
        session.add(coin)
        await session.flush()  # Get the coin.id

        # Create mapping
        await self._create_mapping(
            session,
            coin_id=coin.id,
            source=source,
            source_id=source_id,
            source_symbol=source_symbol,
            source_name=name,
        )

        logger.info(f"Created new Coin: {symbol} (id={coin.id}) from {source.value}:{source_id}")
        return coin.id

    async def _create_mapping(
        self,
        session: AsyncSession,
        coin_id: int,
        source: DataSource,
        source_id: str,
        source_symbol: str,
        source_name: Optional[str] = None,
    ) -> None:
        """Create a source-to-coin mapping."""
        # Check if mapping already exists
        existing_query = select(SourceAssetMapping).where(
            SourceAssetMapping.source == source,
            SourceAssetMapping.source_id == source_id,
        )
        result = await session.execute(existing_query)
        if result.scalar_one_or_none():
            return  # Mapping already exists

        mapping = SourceAssetMapping(
            coin_id=coin_id,
            source=source,
            source_id=source_id,
            source_symbol=source_symbol,
            source_name=source_name,
        )
        session.add(mapping)
        await session.flush()

        logger.debug(f"Created mapping: {source.value}:{source_id} -> coin_id={coin_id}")

    async def _ensure_mapping_exists(
        self,
        session: AsyncSession,
        coin_id: int,
        source: DataSource,
        source_id: str,
        source_symbol: str,
    ) -> None:
        """Ensure a mapping exists, create if not."""
        cache_key = (source, source_id)
        if cache_key in self._mapping_cache:
            return

        await self._create_mapping(
            session,
            coin_id=coin_id,
            source=source,
            source_id=source_id,
            source_symbol=source_symbol,
        )

        self._mapping_cache[cache_key] = coin_id

    def _generate_slug(self, symbol: str, name: str) -> str:
        """Generate a unique slug for a coin."""
        # Use lowercase symbol as primary slug
        base_slug = symbol.lower().strip()

        # If name is different from symbol, include it
        if name and name.upper() != symbol:
            name_part = "".join(c for c in name.lower() if c.isalnum() or c == "-")[:20]
            return f"{base_slug}-{name_part}"

        return base_slug

    async def preload_cache(self, session: AsyncSession) -> None:
        """Preload the resolver cache from database for performance."""
        if self._cache_loaded:
            return

        try:
            # Load all mappings
            mapping_query = select(SourceAssetMapping)
            mapping_result = await session.execute(mapping_query)
            mappings = mapping_result.scalars().all()

            for mapping in mappings:
                cache_key = (mapping.source, mapping.source_id)
                self._mapping_cache[cache_key] = mapping.coin_id

            # Load all coins for symbol cache
            coin_query = select(Coin)
            coin_result = await session.execute(coin_query)
            coins = coin_result.scalars().all()

            for coin in coins:
                self._symbol_cache[coin.symbol] = coin.id

            self._cache_loaded = True
            logger.info(
                f"AssetResolver cache loaded: {len(self._mapping_cache)} mappings, "
                f"{len(self._symbol_cache)} coins"
            )

        except Exception as e:
            logger.warning(f"Failed to preload AssetResolver cache: {e}")

    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._mapping_cache.clear()
        self._symbol_cache.clear()
        self._cache_loaded = False

    def get_cache_stats(self) -> dict:
        """Return cache statistics for monitoring."""
        return {
            "mapping_cache_size": len(self._mapping_cache),
            "symbol_cache_size": len(self._symbol_cache),
            "cache_loaded": self._cache_loaded,
        }


# Singleton instance for application-wide use
asset_resolver = AssetResolver()
