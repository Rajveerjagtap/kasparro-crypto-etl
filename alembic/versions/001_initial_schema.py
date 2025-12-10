"""Initial schema - create all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE data_source_enum AS ENUM ('coinpaprika', 'coingecko', 'csv');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE etl_status_enum AS ENUM ('success', 'failure', 'running');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create raw_data table
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw_data (
            id SERIAL PRIMARY KEY,
            source data_source_enum NOT NULL,
            payload JSONB NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_raw_data_source ON raw_data(source)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_raw_data_created_at ON raw_data(created_at)")
    
    # Create unified_crypto_data table
    op.execute("""
        CREATE TABLE IF NOT EXISTS unified_crypto_data (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            price_usd NUMERIC(20, 8),
            market_cap NUMERIC(30, 2),
            volume_24h NUMERIC(30, 2),
            source data_source_enum NOT NULL,
            ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            timestamp TIMESTAMPTZ NOT NULL,
            CONSTRAINT uq_crypto_symbol_source_timestamp UNIQUE (symbol, source, timestamp)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_unified_crypto_data_symbol ON unified_crypto_data(symbol)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_unified_crypto_data_source ON unified_crypto_data(source)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_unified_crypto_data_timestamp ON unified_crypto_data(timestamp)")
    
    # Create etl_jobs table
    op.execute("""
        CREATE TABLE IF NOT EXISTS etl_jobs (
            id SERIAL PRIMARY KEY,
            source data_source_enum NOT NULL,
            status etl_status_enum NOT NULL,
            last_processed_timestamp TIMESTAMPTZ,
            records_processed INTEGER NOT NULL DEFAULT 0,
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMPTZ,
            error_message VARCHAR(1000)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_etl_jobs_source ON etl_jobs(source)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_etl_jobs_status ON etl_jobs(status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_etl_jobs_started_at ON etl_jobs(started_at)")


def downgrade() -> None:
    op.drop_table('etl_jobs')
    op.drop_table('unified_crypto_data')
    op.drop_table('raw_data')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS etl_status_enum')
    op.execute('DROP TYPE IF EXISTS data_source_enum')
