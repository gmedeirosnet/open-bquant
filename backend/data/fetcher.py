"""
Unified data fetcher — abstracts over multiple market data sources.

Primary source: yfinance (Yahoo Finance)
Cache layer:    Redis (TTL-based)

Usage:
    fetcher = DataFetcher()
    df = await fetcher.get_ohlcv(["PETR4.SA", "VALE3.SA"], start="2022-01-01")
"""

from __future__ import annotations

import asyncio
import json
from functools import partial
from typing import Any

import pandas as pd
import yfinance as yf
from loguru import logger

from backend.core.config import settings


class DataFetcher:
    """Unified interface for fetching market data from multiple sources."""

    # Redis TTL per data type (seconds)
    _TTL = {
        "ohlcv_daily": 3600,       # 1 hour  — updates at market close
        "ohlcv_intraday": 60,      # 1 min   — live data
        "fundamentals": 86400 * 7, # 7 days  — quarterly/annual data
    }

    def __init__(self) -> None:
        self._redis: Any | None = None

    async def _get_redis(self) -> Any:
        """Lazy-initialize async Redis client."""
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    # ─────────────────────────────────────────────────────────────────────────
    # OHLCV
    # ─────────────────────────────────────────────────────────────────────────

    async def get_ohlcv(
        self,
        tickers: list[str],
        start: str,
        end: str = "today",
        interval: str = "1d",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for one or multiple tickers.

        Returns a DataFrame with DatetimeIndex (UTC) and columns:
            Open, High, Low, Close, Volume, Adj Close

        For a single ticker the index is a DatetimeIndex.
        For multiple tickers the columns are a MultiIndex: (field, ticker).
        """
        cache_key = f"ohlcv:{','.join(sorted(tickers))}:{start}:{end}:{interval}"

        if use_cache:
            cached = await self._get_from_cache(cache_key)
            if cached is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached

        logger.info(f"Fetching OHLCV from yfinance: {tickers} {start}→{end}")
        df = await asyncio.get_event_loop().run_in_executor(
            None,
            partial(
                yf.download,
                tickers=tickers if len(tickers) > 1 else tickers[0],
                start=start,
                end=end if end != "today" else None,
                interval=interval,
                auto_adjust=False,  # Keep Adj Close separate
                progress=False,
                threads=True,
            ),
        )

        if df.empty:
            logger.warning(f"No data returned for {tickers}")
            return df

        # Normalise timezone to UTC
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")

        if use_cache:
            ttl = self._TTL["ohlcv_daily"] if interval == "1d" else self._TTL["ohlcv_intraday"]
            await self._set_cache(cache_key, df, ttl=ttl)

        return df

    # ─────────────────────────────────────────────────────────────────────────
    # Fundamentals
    # ─────────────────────────────────────────────────────────────────────────

    async def get_fundamentals(self, ticker: str) -> dict[str, Any]:
        """Fetch key fundamental metrics from yfinance's fast_info + info."""
        cache_key = f"fundamentals:{ticker}"
        cached = await self._get_from_cache(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        logger.info(f"Fetching fundamentals from yfinance: {ticker}")

        def _fetch() -> dict[str, Any]:
            t = yf.Ticker(ticker)
            info = t.info or {}
            return {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "currency": info.get("currency"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "ev_ebitda": info.get("enterpriseToEbitda"),
                "roe": info.get("returnOnEquity"),
                "roa": info.get("returnOnAssets"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "eps": info.get("trailingEps"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "52w_high": info.get("fiftyTwoWeekHigh"),
                "52w_low": info.get("fiftyTwoWeekLow"),
            }

        data = await asyncio.get_event_loop().run_in_executor(None, _fetch)
        await self._set_cache(cache_key, data, ttl=self._TTL["fundamentals"])
        return data

    # ─────────────────────────────────────────────────────────────────────────
    # Cache helpers
    # ─────────────────────────────────────────────────────────────────────────

    async def _get_from_cache(self, key: str) -> pd.DataFrame | dict | None:
        try:
            r = await self._get_redis()
            raw = await r.get(key)
            if raw is None:
                return None
            payload = json.loads(raw)
            if payload.get("_type") == "dataframe":
                return pd.read_json(payload["data"], orient="split")
            return payload
        except Exception as exc:
            logger.warning(f"Cache GET failed ({key}): {exc}")
            return None

    async def _set_cache(
        self,
        key: str,
        data: pd.DataFrame | dict,
        ttl: int = 3600,
    ) -> None:
        try:
            r = await self._get_redis()
            if isinstance(data, pd.DataFrame):
                payload = json.dumps({
                    "_type": "dataframe",
                    "data": data.to_json(orient="split", date_format="iso"),
                })
            else:
                payload = json.dumps(data, default=str)
            await r.setex(key, ttl, payload)
        except Exception as exc:
            logger.warning(f"Cache SET failed ({key}): {exc}")
