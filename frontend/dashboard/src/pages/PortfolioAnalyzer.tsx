export default function PortfolioAnalyzer() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Portfolio Analyzer</h1>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 text-center text-gray-500 space-y-3">
        <div className="text-4xl">⚖️</div>
        <p className="text-gray-300 font-medium">Portfolio Optimizer — Coming in Phase 3</p>
        <p className="text-sm max-w-md mx-auto">
          Optimize portfolios using mean-variance, risk parity, or Black-Litterman via the API
          or directly in notebooks.
        </p>
        <div className="bg-gray-800 rounded-lg p-4 text-left font-mono text-xs text-green-400 max-w-lg mx-auto">
          <div className="text-gray-500 mb-2"># notebooks/portfolio_optimization.ipynb</div>
          <div>from mybquant import portfolio</div>
          <br />
          <div>result = portfolio.optimize(</div>
          <div className="pl-4">tickers=["PETR4.SA", "VALE3.SA", "WEGE3.SA"],</div>
          <div className="pl-4">method="max_sharpe",</div>
          <div className="pl-4">constraints={"{"}{"max_weight": 0.4, "min_weight": 0.0}{"}"},</div>
          <div>)</div>
          <br />
          <div>print(result["weights"])</div>
          <div>print(f"Sharpe: {"{"}result['sharpe_ratio']:.2f{"}"}")</div>
        </div>
      </div>
    </div>
  )
}
