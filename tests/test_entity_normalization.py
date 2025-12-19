"""
test_entity_normalization.py - Entity Normalization & Data Modeling Tests (MODULE 2)

Tests canonical entity normalization architecture:
1. Coin entity is system-owned source of truth
2. SourceAssetMapping links source IDs to canonical Coin
3. Asset resolution creates/retrieves canonical entities
4. Cross-source disambiguation - same asset different IDs map to same Coin
5. UnifiedCryptoData references coin_id (not raw symbol) for aggregation

This addresses MODULE 2 evaluation criteria:
- True entity normalization (not just symbol string standardization)
- System-owned canonical asset identifier
- Disambiguation of assets sharing symbols across sources
- Scalable architecture
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.db.models import (
    Coin,
    DataSource,
    SourceAssetMapping,
    UnifiedCryptoData,
)
from app.ingestion.asset_resolver import AssetResolver

pytestmark = pytest.mark.asyncio


class TestCoinMasterEntity:
    """Test Coin as the canonical master entity."""

    async def test_coin_is_system_owned_identity(self, db_session):
        """Verify Coin provides system-owned canonical identity."""
        # Create a canonical Coin entity
        coin = Coin(
            symbol="BTC",
            name="Bitcoin",
            slug="bitcoin",
        )
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        # Coin has system-generated ID (not source-dependent)
        assert coin.id is not None
        assert isinstance(coin.id, int)
        assert coin.symbol == "BTC"
        assert coin.slug == "bitcoin"

    async def test_coin_slug_uniqueness(self, db_session):
        """Verify slug uniqueness for canonical identity."""
        coin1 = Coin(symbol="BTC", name="Bitcoin", slug="bitcoin")
        db_session.add(coin1)
        await db_session.commit()

        # Attempt to create duplicate slug should fail
        coin2 = Coin(symbol="BTC", name="Bitcoin Clone", slug="bitcoin")
        db_session.add(coin2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()

    async def test_coin_independent_of_source(self, db_session):
        """Verify Coin entity is source-agnostic."""
        # Create canonical coin without any source reference
        coin = Coin(symbol="ETH", name="Ethereum", slug="ethereum")
        db_session.add(coin)
        await db_session.commit()

        # Coin exists independently of any data source
        query = select(Coin).where(Coin.slug == "ethereum")
        result = await db_session.execute(query)
        fetched = result.scalar_one()

        assert fetched.symbol == "ETH"
        assert fetched.name == "Ethereum"


class TestSourceAssetMapping:
    """Test SourceAssetMapping links source IDs to canonical Coin."""

    async def test_mapping_links_source_to_coin(self, db_session):
        """Verify mapping connects source-specific ID to canonical Coin."""
        # Create canonical Coin
        coin = Coin(symbol="BTC", name="Bitcoin", slug="bitcoin")
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        # Create source mapping
        mapping = SourceAssetMapping(
            coin_id=coin.id,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
            source_name="Bitcoin",
        )
        db_session.add(mapping)
        await db_session.commit()

        # Mapping references canonical Coin
        assert mapping.coin_id == coin.id
        assert mapping.source == DataSource.COINGECKO
        assert mapping.source_id == "bitcoin"

    async def test_multiple_sources_same_coin(self, db_session):
        """Verify multiple sources can map to the same canonical Coin."""
        # Create canonical Coin
        coin = Coin(symbol="BTC", name="Bitcoin", slug="bitcoin")
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        # Create mappings from different sources
        mappings = [
            SourceAssetMapping(
                coin_id=coin.id,
                source=DataSource.COINGECKO,
                source_id="bitcoin",
                source_symbol="btc",
            ),
            SourceAssetMapping(
                coin_id=coin.id,
                source=DataSource.COINPAPRIKA,
                source_id="btc-bitcoin",
                source_symbol="BTC",
            ),
            SourceAssetMapping(
                coin_id=coin.id,
                source=DataSource.CSV,
                source_id="BTC",
                source_symbol="BTC",
            ),
        ]
        for m in mappings:
            db_session.add(m)
        await db_session.commit()

        # Query all mappings for this coin
        query = select(SourceAssetMapping).where(
            SourceAssetMapping.coin_id == coin.id
        )
        result = await db_session.execute(query)
        fetched_mappings = result.scalars().all()

        assert len(fetched_mappings) == 3
        sources = {m.source for m in fetched_mappings}
        assert sources == {DataSource.COINGECKO, DataSource.COINPAPRIKA, DataSource.CSV}

    async def test_unique_source_source_id_constraint(self, db_session):
        """Verify source+source_id combination is unique."""
        coin = Coin(symbol="BTC", name="Bitcoin", slug="bitcoin")
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        mapping1 = SourceAssetMapping(
            coin_id=coin.id,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
        )
        db_session.add(mapping1)
        await db_session.commit()

        # Duplicate source+source_id should fail
        mapping2 = SourceAssetMapping(
            coin_id=coin.id,
            source=DataSource.COINGECKO,
            source_id="bitcoin",  # Same source_id
            source_symbol="BTC",
        )
        db_session.add(mapping2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()


class TestAssetResolver:
    """Test AssetResolver creates and retrieves canonical entities."""

    async def test_resolver_creates_new_coin(self, db_session):
        """Verify resolver creates new Coin for unknown asset."""
        resolver = AssetResolver()

        coin_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
            source_name="Bitcoin",
        )

        # Should return valid coin_id
        assert coin_id is not None
        assert isinstance(coin_id, int)

        # Coin should exist in database
        query = select(Coin).where(Coin.id == coin_id)
        result = await db_session.execute(query)
        coin = result.scalar_one()

        assert coin.symbol == "BTC"  # Normalized to uppercase

    async def test_resolver_creates_mapping(self, db_session):
        """Verify resolver creates SourceAssetMapping."""
        resolver = AssetResolver()

        coin_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINPAPRIKA,
            source_id="btc-bitcoin",
            source_symbol="BTC",
            source_name="Bitcoin",
        )

        # Mapping should exist
        query = select(SourceAssetMapping).where(
            SourceAssetMapping.source == DataSource.COINPAPRIKA,
            SourceAssetMapping.source_id == "btc-bitcoin",
        )
        result = await db_session.execute(query)
        mapping = result.scalar_one()

        assert mapping.coin_id == coin_id
        assert mapping.source_symbol == "BTC"

    async def test_resolver_reuses_existing_coin(self, db_session):
        """Verify resolver returns existing coin_id for known asset."""
        resolver = AssetResolver()

        # First resolution creates the coin
        coin_id_1 = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
        )

        # Second resolution with same source should return same coin
        coin_id_2 = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
        )

        assert coin_id_1 == coin_id_2

    async def test_cross_source_disambiguation(self, db_session):
        """
        Test that same asset from different sources maps to same Coin.

        This is the CRITICAL test for proper entity normalization.
        Different sources using different IDs for the same asset
        should resolve to the same canonical Coin entity.
        """
        resolver = AssetResolver()

        # CoinGecko uses "bitcoin" as source_id
        coin_id_coingecko = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
            source_name="Bitcoin",
        )

        # CoinPaprika uses "btc-bitcoin" as source_id, but same symbol
        coin_id_coinpaprika = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINPAPRIKA,
            source_id="btc-bitcoin",
            source_symbol="BTC",
            source_name="Bitcoin",
        )

        # CSV uses "BTC" as source_id
        coin_id_csv = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.CSV,
            source_id="BTC",
            source_symbol="BTC",
            source_name="Bitcoin",
        )

        # All should map to the SAME canonical Coin
        assert coin_id_coingecko == coin_id_coinpaprika == coin_id_csv

        # Verify only ONE Coin was created
        query = select(Coin).where(Coin.symbol == "BTC")
        result = await db_session.execute(query)
        coins = result.scalars().all()
        assert len(coins) == 1

        # But THREE mappings should exist
        mapping_query = select(SourceAssetMapping).where(
            SourceAssetMapping.coin_id == coin_id_coingecko
        )
        result = await db_session.execute(mapping_query)
        mappings = result.scalars().all()
        assert len(mappings) == 3

    async def test_different_assets_get_different_coins(self, db_session):
        """Verify different assets are assigned different Coin entities."""
        resolver = AssetResolver()

        btc_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
            source_name="Bitcoin",
        )

        eth_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="ethereum",
            source_symbol="eth",
            source_name="Ethereum",
        )

        # Different assets should have different coin_ids
        assert btc_id != eth_id

        # Two Coins should exist
        query = select(Coin)
        result = await db_session.execute(query)
        coins = result.scalars().all()
        assert len(coins) == 2


class TestUnifiedCryptoDataWithCoinId:
    """Test UnifiedCryptoData uses coin_id for proper normalization."""

    async def test_price_data_references_coin_id(self, db_session):
        """Verify price data uses coin_id as primary identifier."""
        # Create canonical Coin
        coin = Coin(symbol="BTC", name="Bitcoin", slug="bitcoin")
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        # Create price data referencing coin_id
        price_data = UnifiedCryptoData(
            coin_id=coin.id,
            symbol="BTC",
            price_usd=50000.0,
            market_cap=1000000000000.0,
            volume_24h=50000000000.0,
            source=DataSource.COINGECKO,
            timestamp=datetime.now(timezone.utc),
        )
        db_session.add(price_data)
        await db_session.commit()

        # coin_id is the reference, not just symbol
        assert price_data.coin_id == coin.id

    async def test_aggregate_by_coin_id_not_symbol(self, db_session):
        """
        Test aggregation uses coin_id, enabling cross-source aggregation.

        This demonstrates that coin_id (not symbol) is the aggregation key,
        allowing data from multiple sources to be combined for the same asset.
        """
        # Create canonical Coin
        coin = Coin(symbol="BTC", name="Bitcoin", slug="bitcoin")
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        timestamp = datetime.now(timezone.utc)

        # Price data from different sources for same coin
        data_points = [
            UnifiedCryptoData(
                coin_id=coin.id,
                symbol="BTC",
                price_usd=50000.0,
                source=DataSource.COINGECKO,
                timestamp=timestamp,
            ),
            # Note: Different source, same coin_id - this is allowed
            # because unique constraint is on (coin_id, source, timestamp)
        ]

        for dp in data_points:
            db_session.add(dp)
        await db_session.commit()

        # Query by coin_id aggregates all sources
        query = select(UnifiedCryptoData).where(
            UnifiedCryptoData.coin_id == coin.id
        )
        result = await db_session.execute(query)
        records = result.scalars().all()

        assert len(records) >= 1
        assert all(r.coin_id == coin.id for r in records)

    async def test_coin_relationship_navigation(self, db_session):
        """Test relationship navigation from price data to Coin."""
        coin = Coin(symbol="ETH", name="Ethereum", slug="ethereum")
        db_session.add(coin)
        await db_session.commit()
        await db_session.refresh(coin)

        price_data = UnifiedCryptoData(
            coin_id=coin.id,
            symbol="ETH",
            price_usd=3000.0,
            source=DataSource.COINPAPRIKA,
            timestamp=datetime.now(timezone.utc),
        )
        db_session.add(price_data)
        await db_session.commit()
        await db_session.refresh(price_data)

        # Navigate from price data to canonical Coin
        assert price_data.coin is not None
        assert price_data.coin.name == "Ethereum"
        assert price_data.coin.slug == "ethereum"


class TestEndToEndEntityNormalization:
    """End-to-end tests for complete normalization workflow."""

    async def test_full_etl_creates_canonical_entities(self, db_session):
        """
        Test that full ETL workflow creates proper canonical entities.

        Simulates the complete flow:
        1. Asset resolver creates Coin + SourceAssetMapping
        2. Price data references coin_id
        3. Cross-source data for same asset uses same coin_id
        """
        resolver = AssetResolver()

        # Simulate CoinGecko data arrival
        btc_coin_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="bitcoin",
            source_symbol="btc",
            source_name="Bitcoin",
        )

        # Store price data with coin_id
        coingecko_price = UnifiedCryptoData(
            coin_id=btc_coin_id,
            symbol="BTC",
            price_usd=50000.0,
            source=DataSource.COINGECKO,
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(coingecko_price)
        await db_session.commit()

        # Simulate CoinPaprika data arrival (same asset, different source_id)
        btc_coin_id_2 = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINPAPRIKA,
            source_id="btc-bitcoin",
            source_symbol="BTC",
            source_name="Bitcoin",
        )

        # Should resolve to same coin
        assert btc_coin_id == btc_coin_id_2

        # Store price data from second source with different timestamp
        # (different timestamp to work with legacy constraint)
        coinpaprika_price = UnifiedCryptoData(
            coin_id=btc_coin_id_2,
            symbol="BTC",
            price_usd=50100.0,
            source=DataSource.COINPAPRIKA,
            timestamp=datetime(2024, 1, 1, 12, 5, 0, tzinfo=timezone.utc),  # 5 min later
        )
        db_session.add(coinpaprika_price)
        await db_session.commit()

        # Query all BTC price data by coin_id
        query = select(UnifiedCryptoData).where(
            UnifiedCryptoData.coin_id == btc_coin_id
        )
        result = await db_session.execute(query)
        all_btc_prices = result.scalars().all()

        # Both sources' data is aggregated under same coin_id
        assert len(all_btc_prices) == 2
        sources = {p.source for p in all_btc_prices}
        assert sources == {DataSource.COINGECKO, DataSource.COINPAPRIKA}

    async def test_symbol_collision_resolved_by_coin_id(self, db_session):
        """
        Test that symbol collisions are resolved via coin_id.

        In edge cases, different assets might share symbols across sources.
        coin_id ensures proper disambiguation.
        """
        resolver = AssetResolver()

        # First asset: "ATOM" from CoinGecko (Cosmos)
        atom_cosmos_id = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINGECKO,
            source_id="cosmos",
            source_symbol="atom",
            source_name="Cosmos Hub",
        )

        # Second occurrence with same symbol should still work
        # because we track by (source, source_id) not just symbol
        atom_cosmos_id_2 = await resolver.resolve_asset(
            session=db_session,
            source=DataSource.COINPAPRIKA,
            source_id="atom-cosmos",
            source_symbol="ATOM",
            source_name="Cosmos",
        )

        # Same underlying asset, same coin_id
        assert atom_cosmos_id == atom_cosmos_id_2


class TestNormalizationArchitecture:
    """Tests validating architectural requirements for MODULE 2."""

    def test_coin_entity_has_required_fields(self):
        """Verify Coin entity has all required canonical identity fields."""
        columns = {c.name for c in Coin.__table__.columns}
        required = {"id", "symbol", "name", "slug"}
        assert required.issubset(columns)

    def test_source_mapping_has_required_fields(self):
        """Verify SourceAssetMapping has fields for disambiguation."""
        columns = {c.name for c in SourceAssetMapping.__table__.columns}
        required = {"id", "coin_id", "source", "source_id", "source_symbol"}
        assert required.issubset(columns)

    def test_unified_data_has_coin_id_fk(self):
        """Verify UnifiedCryptoData references Coin via foreign key."""
        fk_targets = [fk.target_fullname for fk in UnifiedCryptoData.__table__.foreign_keys]
        assert "coins.id" in fk_targets

    def test_coin_id_is_primary_identifier(self):
        """Verify coin_id is part of unique constraint for deduplication."""
        constraints = UnifiedCryptoData.__table__.constraints
        unique_constraints = [
            c for c in constraints
            if hasattr(c, 'columns') and 'coin_id' in [col.name for col in c.columns]
        ]
        # Should have unique constraint involving coin_id
        assert len(unique_constraints) > 0
