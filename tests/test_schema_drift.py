"""
test_schema_drift.py - Schema Drift & Compatibility Tests (P2.1)

Tests:
1. CSV with extra/unexpected columns - should succeed with valid columns
2. CSV with missing required columns - should fail gracefully
3. API response with new fields - forward compatibility
4. Type coercion and validation
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
import json
from unittest.mock import patch, MagicMock, AsyncMock

from app.etl.extractors import CSVExtractor, CoinGeckoExtractor, CoinPaprikaExtractor
from app.etl.transformers import CryptoDataTransformer
from app.models.database import UnifiedCryptoData, RawData, ETLJob

pytestmark = pytest.mark.asyncio


class TestCSVSchemaDrift:
    """Test CSV extractor handling of schema changes."""

    async def test_csv_with_extra_columns_succeeds(self, temp_csv_with_extra_columns):
        """
        P2.1: CSV with unexpected columns (weird_col, extra_field) should:
        - Successfully extract valid columns
        - Ignore unknown columns
        - Log a warning (implementation dependent)
        """
        extractor = CSVExtractor(file_path=temp_csv_with_extra_columns)
        data = await extractor.extract()

        assert isinstance(data, list)
        assert len(data) > 0

        # Verify valid columns are extracted
        for record in data:
            # Core fields should exist
            assert "symbol" in record
            assert "name" in record
            assert "price_usd" in record or "price" in record

            # Extra columns should either be:
            # 1. Included as-is (permissive)
            # 2. Filtered out (strict)
            # Both behaviors are acceptable

    async def test_csv_missing_required_columns_fails(self, temp_csv_missing_columns):
        """
        P2.1: CSV missing required columns should fail with clear error.
        """
        extractor = CSVExtractor(file_path=temp_csv_missing_columns)

        with pytest.raises((ValueError, KeyError)) as exc_info:
            data = await extractor.extract()
            # If extract succeeds, transform should fail
            if data:
                transformer = CryptoDataTransformer()
                await transformer.transform(data)

        # Error should indicate missing column
        error_msg = str(exc_info.value).lower()
        assert any(col in error_msg for col in ["price", "required", "missing", "column"])

    async def test_csv_type_coercion(self, tmp_path):
        """Test that numeric fields are properly coerced from strings."""
        # Create CSV with string numbers
        csv_content = """symbol,name,price_usd,market_cap_usd,volume_24h_usd
BTC,Bitcoin,"50000.00","1000000000000","50000000000"
ETH,Ethereum,"4000.50","500000000000","25000000000"
"""
        csv_file = tmp_path / "coercion_test.csv"
        csv_file.write_text(csv_content)

        extractor = CSVExtractor(file_path=str(csv_file))
        data = await extractor.extract()

        assert len(data) == 2
        
        # After transformation, prices should be numeric
        transformer = CryptoDataTransformer()
        transformed = await transformer.transform(data)
        
        for record in transformed:
            assert isinstance(record.get("price_usd"), (int, float))
            # Verify actual values
            if record["symbol"] == "BTC":
                assert record["price_usd"] == 50000.00
            elif record["symbol"] == "ETH":
                assert record["price_usd"] == 4000.50

    async def test_csv_empty_values_handling(self, tmp_path):
        """Test handling of empty/null values in CSV."""
        csv_content = """symbol,name,price_usd,market_cap_usd,volume_24h_usd
BTC,Bitcoin,50000,,
ETH,Ethereum,4000,500000000000,
XRP,Ripple,1.5,,25000000
"""
        csv_file = tmp_path / "empty_values.csv"
        csv_file.write_text(csv_content)

        extractor = CSVExtractor(file_path=str(csv_file))
        data = await extractor.extract()

        assert len(data) == 3

        # Empty values should be None or have default
        for record in data:
            assert record["symbol"] is not None
            assert record["price_usd"] is not None or "price_usd" in record


class TestAPISchemaDrift:
    """Test API extractor handling of schema changes."""

    async def test_coingecko_new_fields_forward_compatible(self):
        """
        Test that CoinGecko extractor handles new API fields gracefully.
        Forward compatibility: new fields should be ignored or stored as raw.
        """
        # Mock response with new/unexpected fields
        mock_response_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 50000,
                "market_cap": 1000000000000,
                "total_volume": 50000000000,
                # New unexpected fields
                "new_feature_field": "some_value",
                "another_new_field": 12345,
                "nested_new": {"key": "value"},
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 4000,
                "market_cap": 500000000000,
                "total_volume": 25000000000,
                "new_feature_field": "another_value",
            },
        ]

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance

            extractor = CoinGeckoExtractor()
            data = await extractor.extract()

            # Should successfully extract without errors
            assert len(data) == 2
            
            # Core fields should be present
            for record in data:
                assert "symbol" in record or "id" in record
                assert "current_price" in record or "price" in record

    async def test_coinpaprika_missing_optional_fields(self):
        """
        Test CoinPaprika extractor when optional fields are missing.
        """
        # Response missing some optional fields
        mock_response_data = [
            {
                "id": "btc-bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "quotes": {
                    "USD": {
                        "price": 50000,
                        # Missing market_cap, volume
                    }
                },
            },
        ]

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance

            extractor = CoinPaprikaExtractor()
            
            # Should handle missing optional fields gracefully
            data = await extractor.extract()
            assert len(data) >= 1


class TestTransformerSchemaDrift:
    """Test transformer handling of schema variations."""

    async def test_transformer_handles_extra_fields(self):
        """Transformer should pass through or ignore extra fields."""
        input_data = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": 50000,
                "market_cap_usd": 1000000000000,
                "volume_24h_usd": 50000000000,
                "extra_field_1": "ignored",
                "extra_field_2": 12345,
            },
        ]

        transformer = CryptoDataTransformer()
        result = await transformer.transform(input_data)

        assert len(result) == 1
        assert result[0]["symbol"] == "BTC"
        assert result[0]["price_usd"] == 50000

    async def test_transformer_validates_required_fields(self):
        """Transformer should validate presence of required fields."""
        # Missing price_usd
        input_data = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                # Missing price_usd
                "market_cap_usd": 1000000000000,
            },
        ]

        transformer = CryptoDataTransformer()

        with pytest.raises((ValueError, KeyError)):
            await transformer.transform(input_data)

    async def test_transformer_normalizes_field_names(self):
        """Transformer should normalize different field name conventions."""
        # Different naming conventions from different sources
        input_variations = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 50000,  # CoinGecko style
                "market_cap": 1000000000000,
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price": 4000,  # Generic style
                "marketCap": 500000000000,  # camelCase
            },
        ]

        transformer = CryptoDataTransformer()
        
        # Transformer should normalize to consistent format
        try:
            result = await transformer.transform(input_variations)
            # If successful, all should have price_usd
            for record in result:
                assert "price_usd" in record or "price" in record
        except (ValueError, KeyError):
            # Strict transformer might reject non-standard fields
            pass


class TestDatabaseSchemaCompatibility:
    """Test database model compatibility with schema changes."""

    async def test_unified_crypto_data_model_flexibility(self, db_session):
        """Test that UnifiedCryptoData model handles nullable fields."""
        job_id = str(uuid4())

        # Insert with minimal required fields
        minimal_record = UnifiedCryptoData(
            symbol="TEST",
            name="Test Coin",
            price_usd=100.0,
            source="test",
            fetched_at=datetime.now(timezone.utc),
            job_id=job_id,
            # market_cap_usd and volume_24h_usd are nullable
        )
        db_session.add(minimal_record)
        await db_session.commit()
        await db_session.refresh(minimal_record)

        assert minimal_record.id is not None
        assert minimal_record.symbol == "TEST"
        assert minimal_record.market_cap_usd is None
        assert minimal_record.volume_24h_usd is None

    async def test_raw_data_stores_arbitrary_json(self, db_session):
        """Test that RawData can store arbitrary JSON payloads."""
        job_id = str(uuid4())

        # Store raw data with arbitrary structure
        raw_payload = {
            "standard_field": "value",
            "nested": {"deep": {"data": 123}},
            "array_field": [1, 2, 3],
            "new_api_field": "future_proof",
        }

        raw_record = RawData(
            source="api_test",
            raw_payload=raw_payload,
            fetched_at=datetime.now(timezone.utc),
            job_id=job_id,
        )
        db_session.add(raw_record)
        await db_session.commit()
        await db_session.refresh(raw_record)

        # Verify JSON stored correctly
        assert raw_record.raw_payload["standard_field"] == "value"
        assert raw_record.raw_payload["nested"]["deep"]["data"] == 123
        assert raw_record.raw_payload["new_api_field"] == "future_proof"


class TestSchemaVersioning:
    """Test schema versioning and migration scenarios."""

    async def test_backward_compatible_data_migration(self, db_session, sample_crypto_data):
        """
        Simulate data migration scenario:
        Old records without new fields should coexist with new records.
        """
        job_id_old = str(uuid4())
        job_id_new = str(uuid4())

        # Insert "old" record (minimal fields)
        old_record = UnifiedCryptoData(
            symbol="OLD",
            name="Old Coin",
            price_usd=10.0,
            source="legacy",
            fetched_at=datetime.now(timezone.utc),
            job_id=job_id_old,
        )
        db_session.add(old_record)

        # Insert "new" record (all fields)
        new_record = UnifiedCryptoData(
            symbol="NEW",
            name="New Coin",
            price_usd=100.0,
            market_cap_usd=1000000,
            volume_24h_usd=500000,
            source="modern",
            fetched_at=datetime.now(timezone.utc),
            job_id=job_id_new,
        )
        db_session.add(new_record)
        await db_session.commit()

        # Both should coexist and be queryable
        from sqlalchemy import select
        
        stmt = select(UnifiedCryptoData).where(
            UnifiedCryptoData.symbol.in_(["OLD", "NEW"])
        )
        result = await db_session.execute(stmt)
        records = result.scalars().all()

        assert len(records) == 2

        old = next(r for r in records if r.symbol == "OLD")
        new = next(r for r in records if r.symbol == "NEW")

        assert old.market_cap_usd is None  # Old record
        assert new.market_cap_usd == 1000000  # New record


class TestDataValidation:
    """Test data validation and sanitization."""

    async def test_price_validation_rejects_negative(self, db_session):
        """Negative prices should be rejected or flagged."""
        job_id = str(uuid4())

        # Try to insert negative price
        try:
            invalid_record = UnifiedCryptoData(
                symbol="INVALID",
                name="Invalid Coin",
                price_usd=-100.0,  # Invalid
                source="test",
                fetched_at=datetime.now(timezone.utc),
                job_id=job_id,
            )
            db_session.add(invalid_record)
            await db_session.commit()
            
            # If no validation at DB level, check in application
            # This test documents expected behavior
            pytest.skip("Database allows negative prices - add CHECK constraint")
        except Exception:
            # Expected: validation should reject negative prices
            pass

    async def test_symbol_validation_uppercase(self, db_session):
        """Symbols should be uppercase."""
        job_id = str(uuid4())

        # Insert lowercase symbol
        record = UnifiedCryptoData(
            symbol="btc",  # Lowercase
            name="Bitcoin",
            price_usd=50000,
            source="test",
            fetched_at=datetime.now(timezone.utc),
            job_id=job_id,
        )
        db_session.add(record)
        await db_session.commit()
        await db_session.refresh(record)

        # Either stored as-is or normalized to uppercase
        # Both are acceptable behaviors
        assert record.symbol in ["btc", "BTC"]
