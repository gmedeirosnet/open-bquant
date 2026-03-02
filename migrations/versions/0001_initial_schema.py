"""Initial schema — ohlcv hypertable, assets, fundamentals.

Revision ID: 0001
Revises:
Create Date: 2026-03-02
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable TimescaleDB
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # OHLCV table
    op.create_table(
        "ohlcv",
        sa.Column("time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("open", sa.Double(), nullable=True),
        sa.Column("high", sa.Double(), nullable=True),
        sa.Column("low", sa.Double(), nullable=True),
        sa.Column("close", sa.Double(), nullable=True),
        sa.Column("volume", sa.Double(), nullable=True),
        sa.Column("adj_close", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("time", "ticker"),
    )
    op.execute(
        "SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE)"
    )
    op.create_index("ohlcv_ticker_time_idx", "ohlcv", ["ticker", sa.text("time DESC")])

    # Assets master table
    op.create_table(
        "assets",
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("exchange", sa.String(20), nullable=True),
        sa.Column("currency", sa.String(10), nullable=True),
        sa.Column("sector", sa.String(100), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("country", sa.String(50), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("ticker"),
    )

    # Fundamentals table
    op.create_table(
        "fundamentals",
        sa.Column("time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("period", sa.String(10), nullable=False),
        sa.Column("revenue", sa.Double(), nullable=True),
        sa.Column("net_income", sa.Double(), nullable=True),
        sa.Column("eps", sa.Double(), nullable=True),
        sa.Column("pe_ratio", sa.Double(), nullable=True),
        sa.Column("pb_ratio", sa.Double(), nullable=True),
        sa.Column("roe", sa.Double(), nullable=True),
        sa.Column("debt_equity", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("time", "ticker", "period"),
    )
    op.execute(
        "SELECT create_hypertable('fundamentals', 'time', if_not_exists => TRUE)"
    )


def downgrade() -> None:
    op.drop_table("fundamentals")
    op.drop_table("assets")
    op.drop_index("ohlcv_ticker_time_idx", table_name="ohlcv")
    op.drop_table("ohlcv")
