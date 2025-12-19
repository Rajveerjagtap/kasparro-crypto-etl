"""Fix unique constraint for coin_id, source, timestamp upserts

Revision ID: 003_fix_unique_constraint
Revises: 002_add_coin_master
Create Date: 2024-12-19 00:00:00.000000

This migration creates a proper unique index on (coin_id, source, timestamp)
to support PostgreSQL ON CONFLICT ... DO UPDATE upsert operations.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '003_fix_unique_constraint'
down_revision: Union[str, None] = '002_add_coin_master'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create unique index on (coin_id, source, timestamp) for upsert support.
    
    PostgreSQL ON CONFLICT requires either:
    - A unique index on the conflict columns, OR  
    - A named unique constraint
    
    We create both for compatibility.
    """
    # Drop any existing constraints/indexes that might conflict
    op.execute("""
        DROP INDEX IF EXISTS ix_uq_coin_source_timestamp;
    """)
    
    op.execute("""
        ALTER TABLE unified_crypto_data 
        DROP CONSTRAINT IF EXISTS uq_coin_source_timestamp;
    """)
    
    op.execute("""
        ALTER TABLE unified_crypto_data 
        DROP CONSTRAINT IF EXISTS uq_symbol_timestamp;
    """)
    
    op.execute("""
        DROP INDEX IF EXISTS uq_symbol_timestamp;
    """)
    
    # Create unique index (required for ON CONFLICT with index_elements)
    # This index supports: ON CONFLICT (coin_id, source, timestamp)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_uq_coin_source_timestamp 
        ON unified_crypto_data (coin_id, source, timestamp)
        WHERE coin_id IS NOT NULL;
    """)


def downgrade() -> None:
    """Remove the unique index."""
    op.execute("DROP INDEX IF EXISTS ix_uq_coin_source_timestamp;")
