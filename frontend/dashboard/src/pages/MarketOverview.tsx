import { useQuery } from '@tanstack/react-query'
import { fetchHealth, fetchFactors } from '@/api/client'

const IBOV_TICKERS = [
  'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA',
  'WEGE3.SA', 'RENT3.SA', 'BBAS3.SA', 'B3SA3.SA', 'SUZB3.SA',
]

export default function MarketOverview() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30_000,
  })

  const { data: factors, isLoading } = useQuery({
    queryKey: ['factors', 'ibovespa', 'momentum_12_1'],
    queryFn: () => fetchFactors('ibovespa', 'momentum_12_1'),
  })

  const momentumScores = factors?.factors[0]?.scores ?? {}
  const momentumRanks = factors?.factors[0]?.rank ?? {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-100">Market Overview</h1>
        <span className={`text-xs px-2 py-1 rounded-full ${
          health?.status === 'ok'
            ? 'bg-green-900 text-green-400'
            : 'bg-red-900 text-red-400'
        }`}>
          API {health?.status ?? 'connecting...'}
        </span>
      </div>

      {/* Universe tiles */}
      <div>
        <h2 className="text-sm font-medium text-gray-400 mb-3">
          Ibovespa — Momentum_12_1 Factor
        </h2>
        {isLoading ? (
          <div className="text-gray-500 text-sm">Loading factor data...</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {IBOV_TICKERS.map((ticker) => {
              const score = momentumScores[ticker]
              const rank = momentumRanks[ticker]
              const hasData = score !== undefined
              const positive = (score ?? 0) > 0
              return (
                <div
                  key={ticker}
                  className={`rounded-lg border p-3 text-sm ${
                    !hasData
                      ? 'border-gray-800 bg-gray-900'
                      : positive
                      ? 'border-green-800 bg-green-950'
                      : 'border-red-800 bg-red-950'
                  }`}
                >
                  <div className="font-mono font-medium text-gray-200 truncate">
                    {ticker.replace('.SA', '')}
                  </div>
                  {hasData ? (
                    <>
                      <div className={`text-lg font-bold ${positive ? 'text-green-400' : 'text-red-400'}`}>
                        {score > 0 ? '+' : ''}{score.toFixed(2)}σ
                      </div>
                      <div className="text-xs text-gray-500">Rank #{rank}</div>
                    </>
                  ) : (
                    <div className="text-gray-600 text-xs">No data</div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Info banner */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-sm text-gray-400">
        <p className="font-medium text-gray-300 mb-1">Getting Started</p>
        <p>
          Open{' '}
          <a
            href="http://localhost:8888/jupyter"
            target="_blank"
            rel="noopener noreferrer"
            className="text-orange-400 hover:underline"
          >
            JupyterLab
          </a>{' '}
          and run <code className="bg-gray-800 px-1 rounded text-xs">notebooks/01_data_exploration.ipynb</code> to
          start exploring data with <code className="bg-gray-800 px-1 rounded text-xs">mybquant</code>.
        </p>
      </div>
    </div>
  )
}
