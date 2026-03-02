"""
mybquant — high-level public API for the BQUANT platform.

Target developer experience (as per CLAUDE.md):

    from mybquant import data, quant, portfolio

    prices = data.get_prices(["PETR4.SA", "VALE3.SA"], start="2020-01-01")
    factors = quant.factors.compute(universe="ibovespa", factors=["momentum_12_1"])
    results = quant.backtest.run(strategy="momentum", ...)
    opt = portfolio.optimize(expected_returns=..., method="max_sharpe")
"""

"""
mybquant — high-level public API for the BQUANT platform.

Target developer experience (as per CLAUDE.md):

    from mybquant import data, quant, portfolio

    prices = data.get_prices(["PETR4.SA", "VALE3.SA"], start="2020-01-01")
    factors = quant.factors.compute(universe="ibovespa", factors=["momentum_12_1"])
    results = quant.backtest.run(strategy="momentum", ...)
    opt = portfolio.optimize(expected_returns=..., method="max_sharpe")
"""

from mybquant import data, quant, portfolio  # noqa: F401 — public API

__version__ = "0.1.0"
__all__ = ["data", "quant", "portfolio"]
