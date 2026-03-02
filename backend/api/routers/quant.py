"""Quant API routes — factors, backtesting, risk endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, HTTPException
from loguru import logger

from backend.data.fetcher import DataFetcher
from backend.quant.factors import FactorEngine
from backend.quant.models import FactorResponse, BacktestRequest, BacktestResponse

router = APIRouter()
_fetcher = DataFetcher()
_factor_engine = FactorEngine()


IBOVESPA_TICKERS = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
    "WEGE3.SA", "RENT3.SA", "BBAS3.SA", "B3SA3.SA", "SUZB3.SA",
]


@router.get("/factors", response_model=FactorResponse)
async def compute_factors(
    universe: Annotated[str, Query(description="Asset universe (e.g. 'ibovespa')")] = "ibovespa",
    factors: Annotated[str, Query(description="Comma-separated factor names")] = "momentum_12_1",
    lookback_years: Annotated[int, Query(ge=1, le=10)] = 3,
) -> FactorResponse:
    """Compute cross-sectional factor scores for a given universe."""
    factor_list = [f.strip() for f in factors.split(",")]
    tickers = IBOVESPA_TICKERS if universe == "ibovespa" else []

    if not tickers:
        raise HTTPException(status_code=400, detail=f"Unknown universe: {universe}")

    try:
        prices = await _fetcher.get_ohlcv(
            tickers=tickers,
            start=f"{2024 - lookback_years}-01-01",
            end="today",
        )
        scores = _factor_engine.compute(prices=prices, factors=factor_list)
        return FactorResponse(universe=universe, factors=scores)
    except Exception as exc:
        logger.error(f"Factor computation failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Submit a backtest job (async — returns job ID for polling)."""
    # In production, this would dispatch a Celery task.
    # For now, returns a stub response.
    return BacktestResponse(
        job_id="stub-job-id",
        status="queued",
        message="Backtesting engine integration in progress.",
    )
