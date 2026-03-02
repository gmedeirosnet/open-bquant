"""
Momentum strategy — 12-1 month cross-sectional momentum.

Buys top-N momentum stocks and shorts bottom-N (long-short),
or goes long-only on the top-N (long-only mode).

Example:
    strategy = MomentumStrategy(n_long=5, n_short=5, lookback=252, skip=21)
    engine = Backtester()
    result = engine.run(strategy, tickers=IBOVESPA, prices=prices, ...)
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Cross-sectional momentum strategy.

    Parameters:
        n_long:     Number of assets to hold long
        n_short:    Number of assets to hold short (0 = long-only)
        lookback:   Formation period in trading days (default: 252 = 12 months)
        skip:       Skip period in trading days (default: 21 = 1 month)
        rebalance:  Rebalancing frequency: 'monthly' | 'weekly' | 'daily'
    """

    def __init__(
        self,
        n_long: int = 5,
        n_short: int = 5,
        lookback: int = 252,
        skip: int = 21,
        rebalance: str = "monthly",
    ) -> None:
        self.n_long = n_long
        self.n_short = n_short
        self.lookback = lookback
        self.skip = skip
        self.rebalance = rebalance

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute 12-1 month momentum scores for each asset at each date.

        Returns a DataFrame of momentum scores (same shape as data).
        """
        # Log returns
        log_prices = np.log(data)

        # Momentum = cumulative return from t-lookback to t-skip
        momentum_scores = pd.DataFrame(index=data.index, columns=data.columns, dtype=float)

        for i in range(self.lookback, len(data)):
            formation_start = i - self.lookback
            formation_end = i - self.skip
            if formation_end <= formation_start:
                continue

            ret = log_prices.iloc[formation_end] - log_prices.iloc[formation_start]
            momentum_scores.iloc[i] = ret

        return momentum_scores.astype(float)

    def size_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """
        Translate momentum signals to portfolio weights.

        Long top-N and short bottom-N on each rebalancing date.
        Equal weights within each bucket.
        """
        weights = pd.DataFrame(0.0, index=signals.index, columns=signals.columns)

        for i, (ts, row) in enumerate(signals.iterrows()):
            if row.isna().all():
                continue

            # Rebalancing logic
            if self.rebalance == "monthly" and i > 0:
                prev_ts = signals.index[i - 1]
                if ts.month == prev_ts.month:
                    weights.iloc[i] = weights.iloc[i - 1]
                    continue

            valid = row.dropna()
            if len(valid) < self.n_long:
                continue

            top_n = valid.nlargest(self.n_long).index
            bottom_n = valid.nsmallest(self.n_short).index if self.n_short > 0 else []

            w = 0.0
            for ticker in top_n:
                weights.at[ts, ticker] = 1.0 / self.n_long
            for ticker in bottom_n:
                weights.at[ts, ticker] = -1.0 / max(self.n_short, 1)

        return weights

    def get_parameters(self) -> dict[str, Any]:
        return {
            "n_long": self.n_long,
            "n_short": self.n_short,
            "lookback": self.lookback,
            "skip": self.skip,
            "rebalance": self.rebalance,
        }
