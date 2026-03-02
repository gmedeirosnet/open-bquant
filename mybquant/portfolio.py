"""mybquant.portfolio — high-level portfolio optimization API for notebooks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from backend.quant.optimizer import PortfolioOptimizer
from mybquant import data as _data

_optimizer = PortfolioOptimizer()


def optimize(
    tickers: list[str] | None = None,
    expected_returns: pd.Series | None = None,
    method: str = "max_sharpe",
    start: str = "2020-01-01",
    end: str = "today",
    risk_free_rate: float = 0.1175,
    constraints: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Optimize portfolio weights using PyPortfolioOpt.

    Args:
        tickers:          Asset universe. Required if expected_returns not given.
        expected_returns: Optional pd.Series(ticker → expected_return) override.
        method:           max_sharpe | min_volatility | risk_parity | equal_weight
        start/end:        Historical price range for covariance estimation.
        risk_free_rate:   Annualized risk-free rate (default: Brazilian Selic ~11.75%).
        constraints:      dict with max_weight, min_weight keys.

    Returns:
        dict with weights (dict[ticker→weight]), expected_return, expected_volatility,
        sharpe_ratio.

    Example:
        result = portfolio.optimize(
            tickers=["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
            method="max_sharpe",
            constraints={"max_weight": 0.4, "min_weight": 0.0},
        )
        print(result["weights"])
        print(f"Expected Sharpe: {result['sharpe_ratio']:.2f}")
    """
    if tickers is None and expected_returns is not None:
        tickers = list(expected_returns.index)

    if not tickers:
        raise ValueError("Provide either tickers or expected_returns with ticker index.")

    prices = _data.get_prices(tickers, start=start, end=end)

    return _optimizer.optimize(
        tickers=tickers,
        method=method,
        start=start,
        end=end,
        risk_free_rate=risk_free_rate,
        constraints=constraints,
        prices=prices,
    )
