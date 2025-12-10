"""ETL Service - Orchestrates extraction, transformation, and loading."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException, ExtractionException
from app.core.logging import logger
from app.db.models import DataSource, ETLJob, ETLStatus, RawData, UnifiedCryptoData
from app.db.session import get_session
from app.ingestion.base import BaseExtractor
from app.ingestion.extractors.coinpaprika import CoinPaprikaExtractor
from app.ingestion.extractors.coingecko import CoinGeckoExtractor
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

    async def upsert_unified_data(
        self,
        session: AsyncSession,
        records: list[UnifiedCryptoDataCreate],
    ) -> int:
        """
        Insert or update unified crypto data using ON CONFLICT DO UPDATE.
        Prevents duplicates based on (symbol, source, timestamp).
        Returns count of affected records.
        """
        if not records:
            return 0

        # Build values for bulk upsert
        values = [
            {
                "symbol": r.symbol,
                "price_usd": r.price_usd,
                "market_cap": r.market_cap,
                "volume_24h": r.volume_24h,
                "source": r.source,
                "timestamp": r.timestamp,
                "ingested_at": datetime.now(timezone.utc),
            }
            for r in records
        ]

        # PostgreSQL upsert using INSERT ... ON CONFLICT
        stmt = insert(UnifiedCryptoData).values(values)

        # Update on conflict: (symbol, source, timestamp)
        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol", "source", "timestamp"],
            set_={
                "price_usd": stmt.excluded.price_usd,
                "market_cap": stmt.excluded.market_cap,
                "volume_24h": stmt.excluded.volume_24h,
                "ingested_at": stmt.excluded.ingested_at,
            },
        )

        await session.execute(stmt)
        return len(values)

    async def run_etl_for_source(
        self,
        source: DataSource,
        force_full: bool = False,
    ) -> ETLJob:
        """
        Execute ETL pipeline for a single source.
        Wraps in transaction - rolls back on failure.
        """
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
                    return job

                # Save raw data for audit
                await self.save_raw_data(session, source, raw_data)

                # Upsert normalized data
                records_processed = await self.upsert_unified_data(session, normalized_data)

                # Commit transaction
                await session.commit()

                # Update job status
                max_timestamp = max(r.timestamp for r in normalized_data)
                await self._update_job_status(
                    job.id, ETLStatus.SUCCESS, records_processed, max_timestamp
                )

                logger.info(f"{source.value}: ETL completed, {records_processed} records processed")
                return job

        except ExtractionException as e:
            logger.error(f"{source.value}: extraction failed - {e.message}")
            await self._update_job_status(
                job.id, ETLStatus.FAILURE, 0, None, e.message
            )
            raise

        except Exception as e:
            logger.error(f"{source.value}: ETL failed - {str(e)}")
            await self._update_job_status(
                job.id, ETLStatus.FAILURE, 0, None, str(e)
            )
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
