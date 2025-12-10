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
    # Create enum types
    data_source_enum = postgresql.ENUM(
        'coinpaprika', 'coingecko', 'csv',
        name='data_source_enum',
        create_type=False
    )
    data_source_enum.create(op.get_bind(), checkfirst=True)
    
    etl_status_enum = postgresql.ENUM(
        'success', 'failure', 'running',
        name='etl_status_enum',
        create_type=False
    )
    etl_status_enum.create(op.get_bind(), checkfirst=True)

    # Create raw_data table
    op.create_table(
        'raw_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source', sa.Enum('coinpaprika', 'coingecko', 'csv', name='data_source_enum'), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_raw_data_source', 'raw_data', ['source'], unique=False)
    op.create_index('ix_raw_data_created_at', 'raw_data', ['created_at'], unique=False)

    # Create unified_crypto_data table
    op.create_table(
        'unified_crypto_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('price_usd', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('market_cap', sa.Numeric(precision=30, scale=2), nullable=True),
        sa.Column('volume_24h', sa.Numeric(precision=30, scale=2), nullable=True),
        sa.Column('source', sa.Enum('coinpaprika', 'coingecko', 'csv', name='data_source_enum'), nullable=False),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol', 'source', 'timestamp', name='uq_crypto_symbol_source_timestamp')
    )
    op.create_index('ix_unified_crypto_data_symbol', 'unified_crypto_data', ['symbol'], unique=False)
    op.create_index('ix_unified_crypto_data_source', 'unified_crypto_data', ['source'], unique=False)
    op.create_index('ix_unified_crypto_data_timestamp', 'unified_crypto_data', ['timestamp'], unique=False)

    # Create etl_jobs table
    op.create_table(
        'etl_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source', sa.Enum('coinpaprika', 'coingecko', 'csv', name='data_source_enum'), nullable=False),
        sa.Column('status', sa.Enum('success', 'failure', 'running', name='etl_status_enum'), nullable=False),
        sa.Column('last_processed_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_etl_jobs_source', 'etl_jobs', ['source'], unique=False)
    op.create_index('ix_etl_jobs_status', 'etl_jobs', ['status'], unique=False)
    op.create_index('ix_etl_jobs_started_at', 'etl_jobs', ['started_at'], unique=False)


def downgrade() -> None:
    op.drop_table('etl_jobs')
    op.drop_table('unified_crypto_data')
    op.drop_table('raw_data')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS etl_status_enum')
    op.execute('DROP TYPE IF EXISTS data_source_enum')
