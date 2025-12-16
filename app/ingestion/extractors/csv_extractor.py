"""CSV file extractor implementation."""

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.core.config import settings
from app.core.exceptions import ExtractionException
from app.core.logging import logger
from app.db.models import DataSource
from app.ingestion.base import BaseExtractor
from app.ingestion.transformers.schemas import RawCryptoRecord
from app.schemas.crypto import UnifiedCryptoDataCreate


class CSVExtractor(BaseExtractor):
    """
    Extractor for local CSV files.
    Expected columns: ticker, price, vol, date
    """

    # Column mapping from CSV to internal schema
    COLUMN_MAP = {
        "ticker": "symbol",
        "price": "price_usd",
        "vol": "volume_24h",
        "date": "timestamp",
    }

    def __init__(self, file_path: Optional[str] = None):
        self.source = DataSource.CSV
        self.file_path = Path(file_path or settings.csv_data_path)

    async def fetch_data(
        self,
        last_processed: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Read data from CSV file.
        Filters records newer than last_processed if provided.
        """
        if not self.file_path.exists():
            raise ExtractionException(
                message=f"CSV file not found: {self.file_path}",
                details={"path": str(self.file_path)},
            )

        try:
            records: list[dict[str, Any]] = []

            with open(self.file_path, "r", encoding="utf-8") as f:
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")

                reader = csv.DictReader(f, dialect=dialect)

                # Normalize column names
                if reader.fieldnames:
                    reader.fieldnames = [col.strip().lower() for col in reader.fieldnames]

                for row in reader:
                    # Map columns to internal names
                    mapped_row = {}
                    for csv_col, internal_col in self.COLUMN_MAP.items():
                        if csv_col in row:
                            mapped_row[internal_col] = row[csv_col]

                    # Include any additional columns
                    for key, value in row.items():
                        if key not in self.COLUMN_MAP and key not in mapped_row:
                            mapped_row[key] = value

                    records.append(mapped_row)

            # Filter by last_processed if provided
            if last_processed:
                filtered = []
                for record in records:
                    timestamp_str = record.get("timestamp")
                    if timestamp_str:
                        try:
                            # Parse timestamp using RawCryptoRecord validator
                            parsed = RawCryptoRecord.model_validate({
                                "symbol": record.get("symbol", "UNKNOWN"),
                                "timestamp": timestamp_str,
                            })
                            if parsed.timestamp > last_processed:
                                filtered.append(record)
                        except Exception:
                            filtered.append(record)
                    else:
                        filtered.append(record)
                records = filtered

            logger.info(f"CSV: read {len(records)} records from {self.file_path}")
            return records

        except ExtractionException:
            raise
        except Exception as e:
            raise ExtractionException(
                message=f"Failed to read CSV file: {str(e)}",
                details={"path": str(self.file_path)},
            )

    def normalize(self, raw_data: list[dict[str, Any]]) -> list[UnifiedCryptoDataCreate]:
        """Transform CSV records to unified schema.
        
        CSV sources may have limited metadata, uses symbol as fallback for name.
        """
        normalized = []

        for item in raw_data:
            try:
                # Build intermediate record with validation
                symbol = item.get("symbol", item.get("ticker", "UNKNOWN"))
                record = RawCryptoRecord(
                    symbol=symbol,
                    price_usd=item.get("price_usd", item.get("price")),
                    market_cap=item.get("market_cap"),
                    volume_24h=item.get("volume_24h", item.get("vol")),
                    timestamp=item.get("timestamp", item.get("date", datetime.now(timezone.utc))),
                )

                # Create unified schema with source metadata
                # CSV may not have distinct source_id, use symbol as fallback
                unified = UnifiedCryptoDataCreate(
                    symbol=record.symbol,
                    source_id=item.get("id") or symbol,  # Use id if available, else symbol
                    name=item.get("name") or symbol,  # Use name if available, else symbol
                    price_usd=record.price_usd,
                    market_cap=record.market_cap,
                    volume_24h=record.volume_24h,
                    source=self.source,
                    timestamp=record.timestamp,
                )
                normalized.append(unified)

            except Exception as e:
                logger.warning(f"Failed to normalize CSV record: {e}")
                continue

        logger.info(f"CSV: normalized {len(normalized)} records")
        return normalized
