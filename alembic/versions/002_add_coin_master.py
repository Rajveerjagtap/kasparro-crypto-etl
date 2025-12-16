"""Add Coin master entity and source mappings for proper normalization

Revision ID: 002_add_coin_master
Revises: 001_initial_schema
Create Date: 2024-12-16 00:00:00.000000

This migration implements proper data normalization by:
1. Creating a 'coins' table as the canonical asset master entity
2. Creating 'source_asset_mappings' to link source-specific IDs to canonical coins
3. Adding 'coin_id' foreign key to 'unified_crypto_data'
4. Migrating existing data to the new schema
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_coin_master'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Implement proper data normalization with Coin master entity.
    """
    # 1. Create coins table (master entity)
    op.execute("""
        CREATE TABLE IF NOT EXISTS coins (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_coins_symbol ON coins(symbol)")

    # 2. Create source_asset_mappings table
    op.execute("""
        CREATE TABLE IF NOT EXISTS source_asset_mappings (
            id SERIAL PRIMARY KEY,
            coin_id INTEGER NOT NULL REFERENCES coins(id) ON DELETE CASCADE,
            source data_source_enum NOT NULL,
            source_id VARCHAR(100) NOT NULL,
            source_symbol VARCHAR(20) NOT NULL,
            source_name VARCHAR(100),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT uq_source_asset_mapping UNIQUE (source, source_id)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_source_mapping_source_symbol 
        ON source_asset_mappings(source, source_symbol)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_source_mapping_coin_id 
        ON source_asset_mappings(coin_id)
    """)

    # 3. Add coin_id column to unified_crypto_data (nullable for migration)
    op.execute("""
        ALTER TABLE unified_crypto_data 
        ADD COLUMN IF NOT EXISTS coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE
    """)

    # 4. Migrate existing data: Create coins from distinct symbols
    op.execute("""
        INSERT INTO coins (symbol, name, slug)
        SELECT DISTINCT 
            UPPER(symbol) as symbol,
            UPPER(symbol) as name,
            LOWER(symbol) as slug
        FROM unified_crypto_data
        WHERE symbol IS NOT NULL
        ON CONFLICT (slug) DO NOTHING
    """)

    # 5. Create source mappings for existing data
    op.execute("""
        INSERT INTO source_asset_mappings (coin_id, source, source_id, source_symbol)
        SELECT DISTINCT
            c.id as coin_id,
            u.source,
            UPPER(u.symbol) as source_id,
            UPPER(u.symbol) as source_symbol
        FROM unified_crypto_data u
        JOIN coins c ON LOWER(c.symbol) = LOWER(u.symbol)
        ON CONFLICT (source, source_id) DO NOTHING
    """)

    # 6. Update unified_crypto_data with coin_id
    op.execute("""
        UPDATE unified_crypto_data u
        SET coin_id = c.id
        FROM coins c
        WHERE LOWER(c.symbol) = LOWER(u.symbol)
        AND u.coin_id IS NULL
    """)

    # 7. Create index on coin_id
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_unified_coin_source 
        ON unified_crypto_data(coin_id, source)
    """)

    # 8. Add unique constraint on (coin_id, source, timestamp)
    # This is the PROPER normalization - keyed on coin_id, not symbol
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE unified_crypto_data 
            ADD CONSTRAINT uq_coin_source_timestamp 
            UNIQUE (coin_id, source, timestamp);
        EXCEPTION
            WHEN duplicate_table THEN null;
            WHEN duplicate_object THEN null;
        END $$;
    """)


def downgrade() -> None:
    """
    Revert to symbol-based schema (not recommended).
    """
    # Remove new constraint
    op.execute("""
        ALTER TABLE unified_crypto_data 
        DROP CONSTRAINT IF EXISTS uq_coin_source_timestamp
    """)

    # Remove coin_id index and column
    op.execute("DROP INDEX IF EXISTS ix_unified_coin_source")
    op.execute("ALTER TABLE unified_crypto_data DROP COLUMN IF EXISTS coin_id")

    # Drop source_asset_mappings table
    op.execute("DROP TABLE IF EXISTS source_asset_mappings")

    # Drop coins table
    op.execute("DROP TABLE IF EXISTS coins")
