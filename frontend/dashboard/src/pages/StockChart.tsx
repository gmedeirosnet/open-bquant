import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { createChart, ColorType } from 'lightweight-charts'
import { fetchOHLCV } from '@/api/client'

const DEFAULT_TICKER = 'PETR4.SA'

export default function StockChart() {
  const [ticker, setTicker] = useState(DEFAULT_TICKER)
  const [input, setInput] = useState(DEFAULT_TICKER)
  const chartRef = useRef<HTMLDivElement>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['ohlcv', ticker],
    queryFn: () => fetchOHLCV(ticker, '2022-01-01'),
    enabled: !!ticker,
  })

  useEffect(() => {
    if (!chartRef.current || !data?.records.length) return

    const chart = createChart(chartRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#030712' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#111827' },
        horzLines: { color: '#111827' },
      },
      width: chartRef.current.clientWidth,
      height: 400,
    })

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    const candleData = data.records
      .filter((r) => r.open && r.high && r.low && r.close)
      .map((r) => ({
        time: r.time.split('T')[0],
        open: r.open!,
        high: r.high!,
        low: r.low!,
        close: r.close!,
      }))

    candleSeries.setData(candleData)
    chart.timeScale().fitContent()

    const handleResize = () => {
      chart.applyOptions({ width: chartRef.current?.clientWidth ?? 800 })
    }
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [data])

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold">Stock Chart</h1>
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === 'Enter' && setTicker(input)}
            placeholder="PETR4.SA"
            className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm font-mono w-32 focus:outline-none focus:border-orange-500"
          />
          <button
            onClick={() => setTicker(input)}
            className="bg-orange-600 hover:bg-orange-500 text-white px-3 py-1.5 rounded text-sm transition-colors"
          >
            Load
          </button>
        </div>
        <span className="text-gray-500 text-sm">{data?.currency}</span>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        {isLoading ? (
          <div className="h-96 flex items-center justify-center text-gray-500">
            Fetching {ticker}...
          </div>
        ) : !data?.records.length ? (
          <div className="h-96 flex items-center justify-center text-gray-500">
            No data for {ticker}
          </div>
        ) : (
          <div ref={chartRef} />
        )}
      </div>

      <p className="text-xs text-gray-600">
        Data via Yahoo Finance. Brazilian tickers: add .SA suffix (e.g. PETR4.SA).
        US tickers: AAPL, MSFT, SPY.
      </p>
    </div>
  )
}
