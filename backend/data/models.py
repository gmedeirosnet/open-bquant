"""
Pydantic v2 request/response models and SQLAlchemy ORM models
for market data (OHLCV, Fundamentals, Assets).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Double, Index, String
from sqlalchemy.dialects.postgresql import TIMESTAMP

from backend.core.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# SQLAlchemy ORM Models
# ─────────────────────────────────────────────────────────────────────────────

class OHLCVOrm(Base):
    """TimescaleDB hypertable — one row per (time, ticker)."""

    __tablename__ = "ohlcv"

    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    ticker = Column(String(20), primary_key=True, nullable=False)
    open = Column(Double)
    high = Column(Double)
    low = Column(Double)
    close = Column(Double)
    volume = Column(Double)
    adj_close = Column(Double)

    __table_args__ = (
        Index("ohlcv_ticker_time_idx", "ticker", time.desc()),
    )


class AssetOrm(Base):
    """Asset master table — metadata for each ticker."""

    __tablename__ = "assets"

    ticker = Column(String(20), primary_key=True)
    name = Column(String(255))
    exchange = Column(String(20))
    currency = Column(String(10))
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Response Models
# ─────────────────────────────────────────────────────────────────────────────

class OHLCVRecord(BaseModel):
    """Single OHLCV bar."""

    model_config = ConfigDict(populate_by_name=True)

    time: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    adj_close: float | None = None


class OHLCVResponse(BaseModel):
    """API response wrapping a list of OHLCV bars for one ticker."""

    ticker: str
    currency: str = "USD"
    records: list[OHLCVRecord] = Field(default_factory=list)

    @classmethod
    def from_dataframe(cls, ticker: str, df: pd.DataFrame) -> "OHLCVResponse":
        """Convert a DataFrame with DatetimeIndex to OHLCVResponse."""
        records = []
        for ts, row in df.iterrows():
            records.append(
                OHLCVRecord(
                    time=ts,
                    open=_safe(row, "Open"),
                    high=_safe(row, "High"),
                    low=_safe(row, "Low"),
                    close=_safe(row, "Close"),
                    volume=_safe(row, "Volume"),
                    adj_close=_safe(row, "Adj Close"),
                )
            )
        return cls(ticker=ticker, records=records)


class FundamentalsResponse(BaseModel):
    """Key fundamental metrics for a single ticker."""

    ticker: str
    data: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _safe(row: Any, col: str) -> float | None:
    """Return float value or None if missing/NaN."""
    import math

    val = row.get(col) if hasattr(row, "get") else getattr(row, col, None)
    if val is None:
        return None
    try:
        f = float(val)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None
