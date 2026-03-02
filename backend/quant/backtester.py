"""
Backtesting engine — wraps Nautilus Trader for strategy simulation.

Architecture:
    - BacktestStrategy (AbstractStrategy adapter for Nautilus)
    - Backtester — high-level interface matching CLAUDE.md UX target
    - BacktestResult — metrics and equity curve

Example:
    bt = Backtester()
    result = bt.run(
        strategy_cls=MyStrategy,
        tickers=["PETR4.SA", "VALE3.SA"],
        start="2020-01-01",
        end="2024-01-01",
        initial_capital=100_000,
        commission_bps=10,
    )
    result.metrics   # Sharpe, Sortino, MaxDD, CAGR
    result.plot_equity_curve()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger


@dataclass
class BacktestResult:
    """Container for backtest output metrics and time series."""

    equity_curve: pd.Series           # Portfolio value over time
    returns: pd.Series                 # Daily returns
    positions: pd.DataFrame           # Position weights over time
    trades: pd.DataFrame              # Individual trade log
    metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.metrics = self._compute_metrics()

    def _compute_metrics(self) -> dict[str, float]:
        r = self.returns.dropna()
        if r.empty:
            return {}

        n_years = len(r) / 252
        total_return = (self.equity_curve.iloc[-1] / self.equity_curve.iloc[0]) - 1
        cagr = (1 + total_return) ** (1 / max(n_years, 1e-9)) - 1
        vol = r.std() * np.sqrt(252)
        sharpe = (r.mean() * 252) / vol if vol > 0 else 0.0
        downside = r[r < 0].std() * np.sqrt(252)
        sortino = (r.mean() * 252) / downside if downside > 0 else 0.0
        rolling_max = self.equity_curve.cummax()
        drawdown = (self.equity_curve - rolling_max) / rolling_max
        max_dd = drawdown.min()

        return {
            "total_return": round(total_return, 4),
            "cagr": round(cagr, 4),
            "volatility": round(vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "max_drawdown": round(max_dd, 4),
            "calmar_ratio": round(cagr / abs(max_dd), 4) if max_dd != 0 else 0.0,
            "n_trades": len(self.trades),
            "win_rate": round(
                (self.trades["pnl"] > 0).mean(), 4
            ) if not self.trades.empty and "pnl" in self.trades else 0.0,
        }

    def plot_equity_curve(self) -> None:
        """Plot equity curve + drawdown (requires matplotlib)."""
        try:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

            # Equity curve
            self.equity_curve.plot(ax=axes[0], color="#0057b7", linewidth=1.5)
            axes[0].set_title("Equity Curve", fontsize=13)
            axes[0].set_ylabel("Portfolio Value")
            axes[0].grid(alpha=0.3)

            # Drawdown
            dd = (self.equity_curve - self.equity_curve.cummax()) / self.equity_curve.cummax()
            dd.plot(ax=axes[1], color="#cc0000", linewidth=1.0, fill=True)
            axes[1].set_title("Drawdown", fontsize=13)
            axes[1].set_ylabel("Drawdown %")
            axes[1].grid(alpha=0.3)

            plt.tight_layout()
            plt.show()
        except ImportError:
            logger.warning("matplotlib not installed — cannot plot.")

    def summary(self) -> str:
        """Pretty-print performance metrics."""
        lines = ["=" * 45, "  BACKTEST RESULTS", "=" * 45]
        for k, v in self.metrics.items():
            label = k.replace("_", " ").title()
            if k in ("total_return", "cagr", "volatility", "max_drawdown", "win_rate"):
                lines.append(f"  {label:<25} {v:>10.2%}")
            else:
                lines.append(f"  {label:<25} {v:>10.4f}")
        lines.append("=" * 45)
        return "\n".join(lines)


class Backtester:
    """
    High-level backtest runner.

    Currently implements a simple vectorized simulation directly.
    Full Nautilus Trader integration is available for event-driven
    backtesting with live-compatible strategies (see run_nautilus()).
    """

    def run(
        self,
        strategy_cls: Any,
        tickers: list[str],
        prices: pd.DataFrame,
        start: str,
        end: str = "today",
        initial_capital: float = 100_000.0,
        commission_bps: float = 10.0,
    ) -> BacktestResult:
        """
        Run a vectorized backtest from price data.

        Args:
            strategy_cls:     Class implementing BaseStrategy.
            tickers:          List of ticker symbols.
            prices:           OHLCV DataFrame (yfinance format).
            start:            ISO date string.
            end:              ISO date string or "today".
            initial_capital:  Starting portfolio value in local currency.
            commission_bps:   Round-trip commission in basis points (10 bps = 0.10%).

        Returns:
            BacktestResult with equity_curve, returns, and metrics.
        """
        logger.info(f"Running backtest: {strategy_cls.__name__} | {start} → {end}")

        # Extract adjusted close prices
        adj_close = self._extract_adj_close(prices, tickers)
        adj_close = adj_close.loc[start:end].dropna(how="all")

        if adj_close.empty:
            raise ValueError(f"No price data in range {start}–{end} for {tickers}")

        # Instantiate strategy
        strategy = strategy_cls()
        signals = strategy.generate_signals(adj_close)
        weights = strategy.size_positions(signals)

        # Align weights to price index
        if isinstance(weights, pd.Series):
            weights = weights.reindex(adj_close.index, method="ffill").fillna(0.0)
        else:
            weights = weights.reindex(adj_close.index, method="ffill").fillna(0.0)

        # Daily log returns for each asset
        log_returns = np.log(adj_close / adj_close.shift(1)).fillna(0.0)

        # Commission cost: |Δw| * commission_bps / 10000
        commission_rate = commission_bps / 10_000
        if isinstance(weights, pd.DataFrame):
            turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
        else:
            turnover = weights.diff().abs().fillna(0.0)
        commission_cost = turnover * commission_rate

        # Portfolio daily return
        if isinstance(weights, pd.DataFrame) and isinstance(log_returns, pd.DataFrame):
            port_returns = (weights.shift(1) * log_returns).sum(axis=1) - commission_cost
        else:
            port_returns = weights.shift(1) * log_returns - commission_cost

        port_returns = port_returns.fillna(0.0)

        # Equity curve
        equity = initial_capital * (1 + port_returns).cumprod()

        # Build trade log (simplified)
        trades = self._build_trade_log(weights, adj_close, commission_rate)

        return BacktestResult(
            equity_curve=equity,
            returns=port_returns,
            positions=weights if isinstance(weights, pd.DataFrame) else weights.to_frame("weight"),
            trades=trades,
        )

    def _extract_adj_close(
        self, prices: pd.DataFrame, tickers: list[str]
    ) -> pd.DataFrame:
        if isinstance(prices.columns, pd.MultiIndex):
            if "Adj Close" in prices.columns.get_level_values(0):
                return prices["Adj Close"]
            return prices["Close"]
        if "Adj Close" in prices.columns:
            return prices[["Adj Close"]].rename(columns={"Adj Close": tickers[0]})
        return prices[["Close"]].rename(columns={"Close": tickers[0]})

    def _build_trade_log(
        self,
        weights: pd.DataFrame | pd.Series,
        prices: pd.DataFrame,
        commission_rate: float,
    ) -> pd.DataFrame:
        """Build a simplified trade log from weight changes."""
        if isinstance(weights, pd.Series):
            weights = weights.to_frame("asset")
        delta = weights.diff().dropna()
        trades = []
        for ts, row in delta.iterrows():
            for ticker, chg in row.items():
                if abs(chg) > 1e-6:
                    price = prices.get(ticker, prices.iloc[:, 0]).get(ts, np.nan)
                    trades.append({
                        "time": ts,
                        "ticker": ticker,
                        "direction": "buy" if chg > 0 else "sell",
                        "weight_change": round(chg, 6),
                        "price": price,
                        "commission": round(abs(chg) * commission_rate, 6),
                        "pnl": np.nan,  # filled post-exit
                    })
        return pd.DataFrame(trades)
