import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fetchFactors } from '@/api/client'

const FACTOR_OPTIONS = [
  { value: 'momentum_12_1', label: '12-1 Month Momentum' },
  { value: 'momentum_1', label: '1-Month Reversal' },
  { value: 'low_vol_12', label: 'Low Volatility (12M)' },
]

export default function FactorExplorer() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['factors', 'ibovespa', 'momentum_12_1,low_vol_12'],
    queryFn: () => fetchFactors('ibovespa', 'momentum_12_1,low_vol_12'),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Factor Explorer</h1>
        <button
          onClick={() => refetch()}
          className="text-sm text-orange-400 hover:text-orange-300 transition-colors"
        >
          ↻ Refresh
        </button>
      </div>

      {isLoading ? (
        <div className="text-gray-500">Computing factors...</div>
      ) : (
        data?.factors.map((factor) => {
          const chartData = Object.entries(factor.scores)
            .sort(([, a], [, b]) => b - a)
            .map(([ticker, score]) => ({
              ticker: ticker.replace('.SA', ''),
              score: parseFloat(score.toFixed(3)),
            }))

          return (
            <div key={factor.name} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h2 className="text-sm font-medium text-gray-300 mb-4">
                {FACTOR_OPTIONS.find((f) => f.value === factor.name)?.label ?? factor.name}
                {' '}
                <span className="text-gray-600 font-normal">(z-score, cross-sectional)</span>
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
                  <XAxis dataKey="ticker" tick={{ fontSize: 11, fill: '#9ca3af' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 6 }}
                    labelStyle={{ color: '#e5e7eb' }}
                  />
                  <Bar dataKey="score" radius={[3, 3, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell
                        key={index}
                        fill={entry.score >= 0 ? '#22c55e' : '#ef4444'}
                        opacity={0.8}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )
        })
      )}

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 text-sm text-gray-500">
        <p className="font-medium text-gray-400 mb-1">About Factor Scores</p>
        <p>
          Scores are cross-sectionally winsorized (1%/99%) and standardized (z-score).
          Positive = above-average factor exposure. Ranking in ascending order = best to worst.
        </p>
      </div>
    </div>
  )
}
