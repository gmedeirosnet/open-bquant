"""
Portfolio optimizer — wraps PyPortfolioOpt.

Supported methods:
    max_sharpe        : Maximize Sharpe ratio (Markowitz efficient frontier)
    min_volatility    : Minimize portfolio volatility
    risk_parity       : Equal risk contribution (ERC)
    equal_weight      : 1/N portfolio (baseline)
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger


class PortfolioOptimizer:
    """Optimize portfolio weights using PyPortfolioOpt."""

    def optimize(
        self,
        tickers: list[str],
        method: str = "max_sharpe",
        start: str = "2020-01-01",
        end: str = "today",
        risk_free_rate: float = 0.1175,
        constraints: dict[str, float] | None = None,
        prices: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        """
        Compute optimal portfolio weights.

        Args:
            tickers:         Asset universe.
            method:          Optimization objective.
            start/end:       Date range for historical data (if prices not given).
            risk_free_rate:  Brazilian Selic rate used for Sharpe calculation.
            constraints:     dict with max_weight, min_weight keys.
            prices:          Pre-fetched adjusted close prices (optional).

        Returns:
            dict with weights, expected_return, expected_volatility, sharpe_ratio.
        """
        from pypfopt import (
            EfficientFrontier,
            HRPOpt,
            expected_returns,
            risk_models,
        )
        from pypfopt.exceptions import OptimizationError

        if prices is None:
            raise ValueError("prices DataFrame is required. Fetch via DataFetcher first.")

        adj_close = self._extract_adj_close(prices)

        mu = expected_returns.mean_historical_return(adj_close, frequency=252)
        S = risk_models.sample_cov(adj_close, frequency=252)

        max_w = constraints.get("max_weight", 0.2) if constraints else 0.2
        min_w = constraints.get("min_weight", 0.0) if constraints else 0.0

        if method == "equal_weight":
            n = len(tickers)
            w = {t: 1.0 / n for t in tickers}
            return {"weights": w, "expected_return": None, "expected_volatility": None, "sharpe_ratio": None}

        if method == "risk_parity":
            hrp = HRPOpt(returns=adj_close.pct_change().dropna())
            weights = hrp.optimize()
            cleaned = hrp.clean_weights()
            return {"weights": cleaned, "expected_return": None, "expected_volatility": None, "sharpe_ratio": None}

        ef = EfficientFrontier(mu, S, weight_bounds=(min_w, max_w))

        try:
            if method == "max_sharpe":
                ef.max_sharpe(risk_free_rate=risk_free_rate)
            elif method == "min_volatility":
                ef.min_volatility()
            else:
                raise ValueError(f"Unknown method: {method}")
        except OptimizationError as exc:
            logger.warning(f"Optimization failed ({method}), falling back to min_volatility: {exc}")
            ef = EfficientFrontier(mu, S, weight_bounds=(min_w, max_w))
            ef.min_volatility()

        cleaned = ef.clean_weights()
        perf = ef.portfolio_performance(risk_free_rate=risk_free_rate, verbose=False)

        return {
            "weights": {k: round(v, 6) for k, v in cleaned.items()},
            "expected_return": round(perf[0], 4),
            "expected_volatility": round(perf[1], 4),
            "sharpe_ratio": round(perf[2], 4),
        }

    def _extract_adj_close(self, prices: pd.DataFrame) -> pd.DataFrame:
        if isinstance(prices.columns, pd.MultiIndex):
            level0 = prices.columns.get_level_values(0)
            if "Adj Close" in level0:
                return prices["Adj Close"]
            if "Close" in level0:
                return prices["Close"]
        if "Adj Close" in prices.columns:
            return prices[["Adj Close"]]
        return prices
