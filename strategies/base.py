"""
Base strategy interface — every trading strategy must implement this ABC.

CLAUDE.md spec:
    class BaseStrategy(ABC):
        def generate_signals(data: pd.DataFrame) -> pd.Series ...
        def size_positions(signals: pd.Series) -> pd.Series ...
        def get_parameters() -> dict ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseStrategy(ABC):
    """
    Abstract base class for all BQUANT trading strategies.

    Subclasses must implement all three abstract methods.
    The Backtester calls them in order:
        1. generate_signals(prices)   → raw signals per asset
        2. size_positions(signals)    → target weight per asset
    """

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series | pd.DataFrame:
        """
        Generate trading signals from price (or factor) data.

        Args:
            data: DataFrame with DatetimeIndex and tickers as columns.
                  Typically adjusted close prices.

        Returns:
            pd.Series (single asset) or pd.DataFrame (universe):
                Values represent signal strength.
                Convention: positive = long, negative = short, 0 = flat.
        """
        ...

    @abstractmethod
    def size_positions(
        self, signals: pd.Series | pd.DataFrame
    ) -> pd.Series | pd.DataFrame:
        """
        Convert signals to target portfolio weights.

        Args:
            signals: Output from generate_signals().

        Returns:
            Target weights. Must sum to ≤ 1.0 for long-only, or be
            dollar-neutral (sum ≈ 0) for long-short.
        """
        ...

    @abstractmethod
    def get_parameters(self) -> dict[str, Any]:
        """Return a dict of strategy parameters for logging / optimization."""
        ...

    def __repr__(self) -> str:
        params = self.get_parameters()
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{self.__class__.__name__}({param_str})"
