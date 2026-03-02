"""
Factor computation engine — cross-sectional factor models.

Supported factors:
    momentum_12_1   : 12-month return excluding last month (Jegadeesh & Titman)
    momentum_1      : 1-month short-term reversal
    value_ep        : Earnings yield (trailing) — requires fundamentals
    quality_roe     : Return on equity z-score
    low_vol_12      : Negative 12-month realized volatility
    size            : Negative log market cap

Usage:
    engine = FactorEngine()
    scores = engine.compute(prices, factors=["momentum_12_1", "low_vol_12"])
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from loguru import logger

from backend.quant.models import FactorScores


SUPPORTED_FACTORS = [
    "momentum_12_1",
    "momentum_1",
    "low_vol_12",
    "size",
]


class FactorEngine:
    """
    Compute cross-sectional factor scores from price data.

    All factors are:
        1. Computed in the time series dimension (scalar per ticker)
        2. Cross-sectionally winsorized at 1%/99%
        3. Standardized (z-score, mean=0, std=1)
        4. Ranked (1 = best)
    """

    def compute(
        self,
        prices: pd.DataFrame,
        factors: list[str],
        as_of: str | None = None,
    ) -> list[FactorScores]:
        """
        Compute factors for all tickers in the prices DataFrame.

        Args:
            prices:  DataFrame with DatetimeIndex and tickers as columns
                     (for single ticker use squeeze() before passing).
            factors: list of factor names.
            as_of:   optional ISO date string — use prices up to this date.

        Returns:
            list of FactorScores, one per requested factor.
        """
        # Normalise input to wide format: rows = dates, cols = tickers
        adj_close = self._extract_adj_close(prices)

        if as_of:
            adj_close = adj_close[adj_close.index <= as_of]

        results: list[FactorScores] = []

        for factor_name in factors:
            if factor_name not in SUPPORTED_FACTORS:
                logger.warning(f"Unknown factor '{factor_name}', skipping.")
                continue
            try:
                raw = self._compute_single(adj_close, factor_name)
                standardized = self._standardize(raw)
                ranked = standardized.rank(ascending=False).astype(int)
                results.append(
                    FactorScores(
                        name=factor_name,
                        scores=standardized.dropna().round(4).to_dict(),
                        rank=ranked.dropna().to_dict(),
                    )
                )
                logger.info(f"Factor '{factor_name}' computed for {len(standardized.dropna())} assets.")
            except Exception as exc:
                logger.error(f"Failed computing factor '{factor_name}': {exc}")

        return results

    # ─────────────────────────────────────────────────────────────────────────
    # Individual factor computations
    # ─────────────────────────────────────────────────────────────────────────

    def _compute_single(self, prices: pd.DataFrame, factor: str) -> pd.Series:
        """Dispatch to the appropriate factor computation method."""
        dispatch = {
            "momentum_12_1": self._momentum_12_1,
            "momentum_1": self._momentum_1,
            "low_vol_12": self._low_vol_12,
            "size": self._size,
        }
        return dispatch[factor](prices)

    def _momentum_12_1(self, prices: pd.DataFrame) -> pd.Series:
        """
        12-1 month price momentum (Jegadeesh & Titman 1993).
        Return over [t-252, t-21] trading days.
        Positive signal = strong past winners.
        """
        if len(prices) < 252:
            logger.warning("Not enough history for momentum_12_1 (need ≥252 days)")
            return pd.Series(dtype=float)

        ret_12m = prices.iloc[-252] if len(prices) >= 252 else prices.iloc[0]
        ret_1m = prices.iloc[-21] if len(prices) >= 21 else prices.iloc[0]
        latest = prices.iloc[-1]

        # Cumulative return from t-252 to t-21
        momentum = (ret_1m / ret_12m) - 1.0
        return momentum

    def _momentum_1(self, prices: pd.DataFrame) -> pd.Series:
        """
        1-month short-term reversal.
        Negative signal (reversal) so we negate for factor direction.
        """
        if len(prices) < 21:
            return pd.Series(dtype=float)
        return -((prices.iloc[-1] / prices.iloc[-21]) - 1.0)

    def _low_vol_12(self, prices: pd.DataFrame) -> pd.Series:
        """
        12-month realized volatility (annualized).
        Negated so that lower-vol assets get higher scores.
        """
        if len(prices) < 252:
            return pd.Series(dtype=float)
        log_returns = np.log(prices / prices.shift(1)).dropna()
        vol = log_returns.iloc[-252:].std() * np.sqrt(252)
        return -vol  # Negate: low vol = good

    def _size(self, prices: pd.DataFrame) -> pd.Series:
        """
        Size factor: negative log price * volume (proxy for market cap).
        Small-cap premia: smaller = higher score.
        Note: ideally use market cap; here we use price as proxy.
        """
        latest_price = prices.iloc[-1]
        return -np.log(latest_price + 1e-9)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_adj_close(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Extract adjusted close prices from a raw yfinance DataFrame.
        Handles both single-ticker (flat columns) and multi-ticker
        (MultiIndex columns: (field, ticker)) formats.
        """
        if isinstance(prices.columns, pd.MultiIndex):
            # Multi-ticker: columns = ("Adj Close", "PETR4.SA"), etc.
            if "Adj Close" in prices.columns.get_level_values(0):
                return prices["Adj Close"]
            if "Close" in prices.columns.get_level_values(0):
                return prices["Close"]
        else:
            # Single ticker
            if "Adj Close" in prices.columns:
                return prices[["Adj Close"]].rename(columns={"Adj Close": prices.columns[0]})
            if "Close" in prices.columns:
                return prices[["Close"]]
        return prices

    def _standardize(self, series: pd.Series) -> pd.Series:
        """Winsorize at 1%/99% then z-score."""
        if series.empty:
            return series
        lo, hi = series.quantile(0.01), series.quantile(0.99)
        clipped = series.clip(lo, hi)
        std = clipped.std()
        if std == 0 or np.isnan(std):
            return clipped - clipped.mean()
        return (clipped - clipped.mean()) / std
