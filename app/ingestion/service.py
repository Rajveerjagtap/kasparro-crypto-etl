"""ETL Service - Orchestrates extraction, transformation, and loading.

Implements proper entity normalization via AssetResolver - maps source-specific
asset identifiers to canonical Coin entities for aggregation and deduplication.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException, ExtractionException
from app.core.logging import logger
from app.core.middleware import metrics_collector
from app.db.models import DataSource, ETLJob, ETLStatus, RawData, UnifiedCryptoData
from app.db.session import get_session
from app.ingestion.asset_resolver import AssetResolver
from app.ingestion.base import BaseExtractor
from app.ingestion.drift import DriftDetector
from app.ingestion.extractors.coingecko import CoinGeckoExtractor
from app.ingestion.extractors.coinpaprika import CoinPaprikaExtractor
from app.ingestion.extractors.csv_extractor import CSVExtractor
from app.schemas.crypto import UnifiedCryptoDataCreate


class ETLService:
    """
    Orchestrates ETL pipeline with incremental loading and idempotency.
    Handles checkpointing, upserts, and transactional safety.
    """

    EXTRACTORS: dict[DataSource, type[BaseExtractor]] = {
        DataSource.COINPAPRIKA: CoinPaprikaExtractor,
        DataSource.COINGECKO: CoinGeckoExtractor,
        DataSource.CSV: CSVExtractor,
    }

    def __init__(self):
        self._extractors: dict[DataSource, BaseExtractor] = {}
        # Initialize drift detectors per source
        self.drift_detectors = {
            DataSource.COINPAPRIKA: DriftDetector(expected_columns=["id", "symbol", "name", "quotes"]),
            DataSource.COINGECKO: DriftDetector(expected_columns=["id", "symbol", "name", "current_price"]),
            DataSource.CSV: DriftDetector(expected_columns=["ticker", "price", "vol", "date"]),
        }
        # Asset resolver for canonical entity normalization
        self.asset_resolver = AssetResolver()

    def get_extractor(self, source: DataSource) -> BaseExtractor:
        """Get or create extractor instance for source."""
        if source not in self._extractors:
            extractor_cls = self.EXTRACTORS.get(source)
            if not extractor_cls:
                raise ValueError(f"No extractor registered for source: {source}")
            self._extractors[source] = extractor_cls()
        return self._extractors[source]

    async def get_last_processed_timestamp(
        self,
        session: AsyncSession,
        source: DataSource,
    ) -> Optional[datetime]:
        """
        Query ETLJob table for last successful run timestamp.
        Used for incremental loading.
        """
        query = (
            select(ETLJob.last_processed_timestamp)
            .where(ETLJob.source == source)
            .where(ETLJob.status == ETLStatus.SUCCESS)
            .order_by(ETLJob.completed_at.desc())
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def create_etl_job(
        self,
        session: AsyncSession,
        source: DataSource,
    ) -> ETLJob:
        """Create new ETL job record with RUNNING status."""
        job = ETLJob(
            source=source,
            status=ETLStatus.RUNNING,
            records_processed=0,
        )
        session.add(job)
        await session.flush()
        return job

    async def save_raw_data(
        self,
        session: AsyncSession,
        source: DataSource,
        raw_data: list[dict[str, Any]],
    ) -> None:
        """Store raw data blobs for auditability."""
        if not raw_data:
            return

        for item in raw_data:
            raw_record = RawData(
                source=source,
                payload=item,
            )
            session.add(raw_record)

        await session.flush()
        logger.debug(f"Saved {len(raw_data)} raw records for {source.value}")

    async def resolve_and_upsert_unified_data(
        self,
        session: AsyncSession,
        records: list[UnifiedCryptoDataCreate],
        raw_data: list[dict],
        source: DataSource,
    ) -> int:
        """Resolve assets to canonical Coin entities and upsert unified data.

        This implements proper entity normalization:
        1. For each record, resolve source_id + symbol to a canonical Coin
        2. Use coin_id (not raw symbol) as the primary identifier
        3. Prevents duplicates based on (coin_id, timestamp)

        Returns count of affected records.
        """
        if not records:
            return 0

        # Build source_id map from raw_data for asset resolution
        source_id_map = self._build_source_id_map(raw_data, source)

        # Resolve each record to a canonical coin
        resolved_records = []
        for record in records:
            # Get source-specific ID from raw data
            source_id = source_id_map.get(record.symbol)

            # Resolve to canonical coin entity (returns coin_id)
            coin_id = await self.asset_resolver.resolve_asset(
                session=session,
                source=source,
                source_id=source_id or record.symbol,  # Fallback to symbol if no source_id
                source_symbol=record.symbol,
                source_name=record.name,
            )

            if coin_id:
                resolved_records.append((coin_id, record))
            else:
                logger.warning(f"Could not resolve asset: {record.symbol} from {source.value}")

        if not resolved_records:
            return 0

        # Deduplicate by (coin_id, timestamp) - last record wins
        unique_records = {
            (coin_id, r.timestamp): (coin_id, r)
            for coin_id, r in resolved_records
        }
        deduplicated = list(unique_records.values())

        if len(deduplicated) < len(resolved_records):
            logger.warning(
                f"Dropped {len(resolved_records) - len(deduplicated)} duplicate records before upsert."
            )

        # Build values for bulk upsert with coin_id
        values = [
            {
                "coin_id": coin_id,
                "symbol": record.symbol,  # Keep symbol for readability/queries
                "price_usd": record.price_usd,
                "market_cap": record.market_cap,
                "volume_24h": record.volume_24h,
                "source": record.source,
                "timestamp": record.timestamp,
                "ingested_at": datetime.now(timezone.utc),
            }
            for coin_id, record in deduplicated
        ]

        # PostgreSQL upsert using INSERT ... ON CONFLICT
        stmt = insert(UnifiedCryptoData).values(values)

        # Update on conflict: (coin_id, timestamp) - canonical entity deduplication
        stmt = stmt.on_conflict_do_update(
            index_elements=["coin_id", "timestamp"],
            set_={
                "price_usd": stmt.excluded.price_usd,
                "market_cap": stmt.excluded.market_cap,
                "volume_24h": stmt.excluded.volume_24h,
                "source": stmt.excluded.source,
                "ingested_at": stmt.excluded.ingested_at,
            },
        )

        await session.execute(stmt)
        return len(values)

    def _build_source_id_map(
        self,
        raw_data: list[dict],
        source: DataSource
    ) -> dict[str, str]:
        """
        Extract source-specific IDs from raw data.
        Maps symbol -> source_id for asset resolution.
        """
        source_id_map = {}

        for item in raw_data:
            if source == DataSource.COINGECKO:
                # CoinGecko: id is the unique identifier, symbol is ticker
                source_id = item.get("id")
                symbol = item.get("symbol", "").upper()
            elif source == DataSource.COINPAPRIKA:
                # CoinPaprika: id is unique (e.g., "btc-bitcoin")
                source_id = item.get("id")
                symbol = item.get("symbol", "").upper()
            elif source == DataSource.CSV:
                # CSV: use ticker/symbol as source_id
                source_id = item.get("ticker") or item.get("symbol")
                symbol = (item.get("ticker") or item.get("symbol", "")).upper()
            else:
                continue

            if source_id and symbol:
                source_id_map[symbol] = source_id

        return source_id_map

    async def run_etl_for_source(
        self,
        source: DataSource,
        force_full: bool = False,
    ) -> ETLJob:
        """
        Execute ETL pipeline for a single source.
        Wraps in transaction - rolls back on failure.
        """
        start_time = time.perf_counter()
        async with get_session() as session:
            job = await self.create_etl_job(session, source)
            await session.commit()

        try:
            async with get_session() as session:
                # Get checkpoint for incremental loading
                last_processed: Optional[datetime] = None
                if not force_full:
                    last_processed = await self.get_last_processed_timestamp(session, source)
                    if last_processed:
                        logger.info(f"{source.value}: incremental load from {last_processed}")

                # Extract and normalize
                extractor = self.get_extractor(source)
                raw_data, normalized_data = await extractor.extract(last_processed)

                if not normalized_data:
                    logger.info(f"{source.value}: no new data to process")
                    await self._update_job_status(
                        job.id, ETLStatus.SUCCESS, 0, None
                    )
                    job.status = ETLStatus.SUCCESS
                    metrics_collector.increment_etl_run(source.value, "success")
                    metrics_collector.set_etl_duration(source.value, time.perf_counter() - start_time)
                    return job

                # --- Data Drift Detection ---
                if raw_data:
                    try:
                        df_raw = pd.DataFrame(raw_data)
                        # Use source-specific detector
                        detector = self.drift_detectors.get(source)
                        if detector:
                            detector.detect_drift(df_raw)
                        else:
                            logger.warning(f"No drift detector configured for {source.value}")
                    except Exception as e:
                        logger.warning(f"Drift detection skipped/failed: {e}")

                # --- Entity Normalization via AssetResolver ---
                # Instead of simple symbol string normalization, we resolve each asset
                # to a canonical Coin entity using source-specific identifiers.
                # This happens in resolve_and_upsert_unified_data()

                # Save raw data for audit
                await self.save_raw_data(session, source, raw_data)

                # Resolve assets and upsert normalized data with coin_id
                records_processed = await self.resolve_and_upsert_unified_data(
                    session, normalized_data, raw_data, source
                )

                # Commit transaction
                await session.commit()

                # Update job status
                max_timestamp = max(r.timestamp for r in normalized_data)
                await self._update_job_status(
                    job.id, ETLStatus.SUCCESS, records_processed, max_timestamp
                )

                # Update local object for return
                job.status = ETLStatus.SUCCESS
                job.records_processed = records_processed
                job.last_processed_timestamp = max_timestamp

                logger.info(f"{source.value}: ETL completed, {records_processed} records processed")
                metrics_collector.increment_etl_run(source.value, "success")
                metrics_collector.set_etl_duration(source.value, time.perf_counter() - start_time)
                return job

        except ExtractionException as e:
            logger.error(f"{source.value}: extraction failed - {e.message}")
            await self._update_job_status(
                job.id, ETLStatus.FAILURE, 0, None, e.message
            )
            job.status = ETLStatus.FAILURE
            job.error_message = e.message
            metrics_collector.increment_etl_run(source.value, "failure")
            metrics_collector.set_etl_duration(source.value, time.perf_counter() - start_time)
            raise

        except Exception as e:
            logger.error(f"{source.value}: ETL failed - {str(e)}")
            await self._update_job_status(
                job.id, ETLStatus.FAILURE, 0, None, str(e)
            )
            job.status = ETLStatus.FAILURE
            job.error_message = str(e)
            metrics_collector.increment_etl_run(source.value, "failure")
            metrics_collector.set_etl_duration(source.value, time.perf_counter() - start_time)
            raise DatabaseException(
                message=f"ETL failed for {source.value}",
                details={"error": str(e)},
            )

    async def _update_job_status(
        self,
        job_id: int,
        status: ETLStatus,
        records_processed: int,
        last_processed_timestamp: Optional[datetime],
        error_message: Optional[str] = None,
    ) -> None:
        """Update ETL job record with final status."""
        async with get_session() as session:
            query = select(ETLJob).where(ETLJob.id == job_id)
            result = await session.execute(query)
            job = result.scalar_one()

            job.status = status
            job.records_processed = records_processed
            job.completed_at = datetime.now(timezone.utc)
            job.last_processed_timestamp = last_processed_timestamp

            # Truncate error message to fit in DB column (VARCHAR(1000))
            if error_message and len(error_message) > 990:
                job.error_message = error_message[:990] + "..."
            else:
                job.error_message = error_message

            await session.commit()

    async def run_all_sources(
        self,
        sources: Optional[list[DataSource]] = None,
        force_full: bool = False,
        parallel: bool = True,
    ) -> dict[DataSource, ETLJob]:
        """
        Execute ETL for multiple sources.
        Can run in parallel or sequential mode.
        """
        target_sources = sources or list(DataSource)
        results: dict[DataSource, ETLJob] = {}

        if parallel:
            tasks = [
                self.run_etl_for_source(source, force_full)
                for source in target_sources
            ]
            completed = await asyncio.gather(*tasks, return_exceptions=True)

            for source, result in zip(target_sources, completed):
                if isinstance(result, Exception):
                    logger.error(f"{source.value}: {result}")
                else:
                    results[source] = result
        else:
            for source in target_sources:
                try:
                    job = await self.run_etl_for_source(source, force_full)
                    results[source] = job
                except Exception as e:
                    logger.error(f"{source.value}: {e}")

        return results


# Singleton instance
etl_service = ETLService()
