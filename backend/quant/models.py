"""Pydantic models for quant API (factors, backtesting, optimization)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Factors
# ─────────────────────────────────────────────────────────────────────────────

class FactorScores(BaseModel):
    """Cross-sectional factor scores for one factor."""

    name: str
    scores: dict[str, float]          # ticker → z-score
    rank: dict[str, int]              # ticker → rank (1 = best)


class FactorResponse(BaseModel):
    universe: str
    factors: list[FactorScores]


# ─────────────────────────────────────────────────────────────────────────────
# Backtesting
# ─────────────────────────────────────────────────────────────────────────────

class BacktestRequest(BaseModel):
    strategy: str = Field(..., description="Strategy name / class path")
    tickers: list[str] = Field(..., min_length=1)
    start: str = Field(..., description="ISO date YYYY-MM-DD")
    end: str = Field(default="today")
    params: dict[str, Any] = Field(default_factory=dict)
    initial_capital: float = Field(default=100_000.0, ge=1.0)
    commission_bps: float = Field(default=10.0, ge=0.0, description="Commission in basis points")


class BacktestResponse(BaseModel):
    job_id: str
    status: str   # queued | running | completed | failed
    message: str | None = None
    result: dict[str, Any] | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio Optimization
# ─────────────────────────────────────────────────────────────────────────────

class OptimizationConstraints(BaseModel):
    max_weight: float = Field(default=0.2, ge=0.0, le=1.0)
    min_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    max_sector_weight: float = Field(default=0.4, ge=0.0, le=1.0)


class OptimizationRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2)
    method: str = Field(
        default="max_sharpe",
        description="max_sharpe | min_volatility | risk_parity | equal_weight",
    )
    start: str = Field(default="2020-01-01")
    end: str = Field(default="today")
    risk_free_rate: float = Field(default=0.1175, description="Brazilian Selic rate (annualized)")
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints)


class OptimizationResponse(BaseModel):
    method: str
    weights: dict[str, float]
    expected_return: float | None = None
    expected_volatility: float | None = None
    sharpe_ratio: float | None = None
