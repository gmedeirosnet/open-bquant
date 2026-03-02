"""mybquant.data — high-level synchronous data access API for notebooks."""

from __future__ import annotations

import asyncio
from typing import Any

import pandas as pd

from backend.data.fetcher import DataFetcher

_fetcher = DataFetcher()


def _run(coro: Any) -> Any:
    """Run a coroutine synchronously — safe to call from Jupyter notebooks."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Jupyter: use nest_asyncio or create a new task
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def get_prices(
    tickers: list[str],
    start: str = "2020-01-01",
    end: str = "today",
    interval: str = "1d",
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Fetch adjusted close prices for one or more tickers.

    Returns:
        DataFrame with DatetimeIndex (UTC) and tickers as columns.
        Single ticker: flat column names.
        Multiple tickers: MultiIndex columns (field, ticker).

    Example:
        prices = data.get_prices(["PETR4.SA", "VALE3.SA"], start="2022-01-01")
        adj_close = prices["Adj Close"]
    """
    return _run(_fetcher.get_ohlcv(tickers, start=start, end=end, interval=interval, use_cache=use_cache))


def get_ohlcv(
    tickers: list[str],
    start: str = "2020-01-01",
    end: str = "today",
    interval: str = "1d",
) -> pd.DataFrame:
    """Alias for get_prices — returns full OHLCV data."""
    return get_prices(tickers, start=start, end=end, interval=interval)


def get_fundamentals(ticker: str) -> dict[str, Any]:
    """
    Fetch fundamental metrics for a single ticker.

    Returns:
        dict with keys: pe_ratio, pb_ratio, roe, revenue, market_cap, etc.
    """
    return _run(_fetcher.get_fundamentals(ticker))
