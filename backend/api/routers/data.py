"""Data API routes — OHLCV, fundamentals, universe endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.data.fetcher import DataFetcher
from backend.data.models import OHLCVResponse, FundamentalsResponse

router = APIRouter()
_fetcher = DataFetcher()


@router.get("/ohlcv", response_model=OHLCVResponse)
async def get_ohlcv(
    ticker: Annotated[str, Query(description="Ticker symbol (e.g. PETR4.SA, AAPL)")],
    start: Annotated[date, Query(description="Start date (YYYY-MM-DD)")],
    end: Annotated[date | None, Query(description="End date (YYYY-MM-DD)")] = None,
    db: AsyncSession = Depends(get_db),
) -> OHLCVResponse:
    """
    Return OHLCV time series for a single ticker.

    - Data is fetched from yfinance and cached in Redis.
    - Prices are adjusted for corporate actions (splits, dividends).
    """
    try:
        df = await _fetcher.get_ohlcv(
            tickers=[ticker],
            start=start.isoformat(),
            end=end.isoformat() if end else "today",
        )
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        return OHLCVResponse.from_dataframe(ticker, df)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error fetching OHLCV for {ticker}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/fundamentals", response_model=FundamentalsResponse)
async def get_fundamentals(
    ticker: Annotated[str, Query(description="Ticker symbol")],
    db: AsyncSession = Depends(get_db),
) -> FundamentalsResponse:
    """Return key fundamental metrics for a ticker from yfinance."""
    try:
        data = await _fetcher.get_fundamentals(ticker)
        return FundamentalsResponse(ticker=ticker, data=data)
    except Exception as exc:
        logger.error(f"Error fetching fundamentals for {ticker}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
