"""mybquant.quant — high-level quant API for notebooks."""

from __future__ import annotations

from typing import Any

import pandas as pd

from backend.quant.factors import FactorEngine
from backend.quant.backtester import Backtester, BacktestResult
from mybquant import data as _data

_factor_engine = FactorEngine()
_backtester = Backtester()


class _Factors:
    """Factor computation interface."""

    def compute(
        self,
        universe: str | list[str],
        factors: list[str] | str,
        start: str = "2020-01-01",
        end: str = "today",
        as_of: str | None = None,
    ) -> dict[str, Any]:
        """
        Compute cross-sectional factor scores for a universe.

        Args:
            universe:  Predefined universe name (e.g. 'ibovespa') or list of tickers.
            factors:   Factor name(s) to compute.
            start/end: Historical data range for factor computation.
            as_of:     Optional cutoff date for point-in-time computation.

        Returns:
            dict mapping factor_name → pd.Series(ticker → z-score).

        Example:
            scores = quant.factors.compute("ibovespa", ["momentum_12_1", "low_vol_12"])
            scores["momentum_12_1"]  # pd.Series: PETR4.SA → 1.23, ...
        """
        from backend.api.routers.quant import IBOVESPA_TICKERS

        if isinstance(factors, str):
            factors = [factors]

        tickers = IBOVESPA_TICKERS if universe == "ibovespa" else list(universe)
        prices = _data.get_prices(tickers, start=start, end=end)

        factor_scores = _factor_engine.compute(prices=prices, factors=factors, as_of=as_of)

        return {
            fs.name: pd.Series(fs.scores)
            for fs in factor_scores
        }


class _Backtest:
    """Backtesting interface."""

    def run(
        self,
        strategy: str | Any,
        tickers: list[str],
        start: str,
        end: str = "today",
        initial_capital: float = 100_000.0,
        commission_bps: float = 10.0,
        params: dict[str, Any] | None = None,
    ) -> BacktestResult:
        """
        Run a backtest.

        Args:
            strategy:         Strategy name (e.g. 'momentum') or class.
            tickers:          List of tickers.
            start/end:        Backtest date range.
            initial_capital:  Starting capital.
            commission_bps:   Commission in basis points.
            params:           Strategy constructor kwargs.

        Example:
            result = quant.backtest.run(
                "momentum",
                tickers=["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
                start="2021-01-01",
            )
            print(result.summary())
            result.plot_equity_curve()
        """
        params = params or {}

        # Resolve strategy
        strategy_cls = self._resolve_strategy(strategy)

        # Fetch prices
        prices = _data.get_prices(tickers, start=start, end=end)

        return _backtester.run(
            strategy_cls=strategy_cls,
            tickers=tickers,
            prices=prices,
            start=start,
            end=end,
            initial_capital=initial_capital,
            commission_bps=commission_bps,
        )

    def _resolve_strategy(self, strategy: str | Any) -> Any:
        if not isinstance(strategy, str):
            return strategy  # already a class
        _registry = {
            "momentum": "strategies.momentum.MomentumStrategy",
        }
        path = _registry.get(strategy.lower())
        if path is None:
            raise ValueError(f"Unknown strategy: '{strategy}'. Available: {list(_registry)}")
        module_path, class_name = path.rsplit(".", 1)
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)


factors = _Factors()
backtest = _Backtest()
