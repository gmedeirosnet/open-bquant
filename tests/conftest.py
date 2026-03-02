"""
Pytest configuration and shared fixtures for the BQUANT test suite.
"""
from __future__ import annotations

import asyncio
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest


# ── Event Loop ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the whole test session (async tests)."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ── Price Data Fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def sample_tickers() -> list[str]:
    return ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"]


@pytest.fixture(scope="session")
def sample_prices(sample_tickers: list[str]) -> pd.DataFrame:
    """
    Generate synthetic daily OHLCV-style close prices for testing.
    Uses geometric Brownian motion with realistic parameters.
    """
    rng = np.random.default_rng(42)
    n_days = 504  # ~2 years of trading days
    n_assets = len(sample_tickers)

    # GBM parameters
    mu_annual = 0.12        # 12% annual drift
    sigma_annual = 0.25     # 25% annual vol
    dt = 1 / 252

    # Simulate correlated returns
    corr_matrix = np.full((n_assets, n_assets), 0.4)
    np.fill_diagonal(corr_matrix, 1.0)
    chol = np.linalg.cholesky(corr_matrix)

    z = rng.standard_normal((n_days, n_assets))
    correlated_z = z @ chol.T

    daily_returns = np.exp(
        (mu_annual - 0.5 * sigma_annual**2) * dt
        + sigma_annual * np.sqrt(dt) * correlated_z
    )

    # Starting prices
    start_prices = np.array([35.0, 75.0, 28.0, 20.0, 15.0])
    price_array = np.cumprod(daily_returns, axis=0) * start_prices

    end_date = date.today()
    start_date = end_date - timedelta(days=n_days + 200)
    bdays = pd.bdate_range(start=start_date, periods=n_days, freq="B")

    prices = pd.DataFrame(price_array, index=bdays, columns=sample_tickers)
    return prices


@pytest.fixture(scope="session")
def sample_returns(sample_prices: pd.DataFrame) -> pd.DataFrame:
    """Log returns from sample prices."""
    return np.log(sample_prices / sample_prices.shift(1)).dropna()
