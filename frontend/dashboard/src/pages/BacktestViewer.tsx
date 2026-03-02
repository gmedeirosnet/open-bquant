export default function BacktestViewer() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Backtest Viewer</h1>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 text-center text-gray-500 space-y-3">
        <div className="text-4xl">📊</div>
        <p className="text-gray-300 font-medium">Backtest Runner — Coming in Phase 2</p>
        <p className="text-sm max-w-md mx-auto">
          Run backtests directly from JupyterLab using the <code className="bg-gray-800 px-1 rounded">mybquant</code> API,
          or submit jobs via the REST API.
        </p>
        <div className="bg-gray-800 rounded-lg p-4 text-left font-mono text-xs text-green-400 max-w-lg mx-auto">
          <div className="text-gray-500 mb-2"># notebooks/01_data_exploration.ipynb</div>
          <div>from mybquant import quant</div>
          <br />
          <div>result = quant.backtest.run(</div>
          <div className="pl-4">strategy="momentum",</div>
          <div className="pl-4">tickers=["PETR4.SA", "VALE3.SA"],</div>
          <div className="pl-4">start="2021-01-01",</div>
          <div>)</div>
          <br />
          <div>print(result.summary())</div>
          <div>result.plot_equity_curve()</div>
        </div>
      </div>
    </div>
  )
}
