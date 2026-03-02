import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ─── Data endpoints ───────────────────────────────────────────────────────────

export interface OHLCVRecord {
  time: string
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  volume: number | null
  adj_close: number | null
}

export interface OHLCVResponse {
  ticker: string
  currency: string
  records: OHLCVRecord[]
}

export const fetchOHLCV = (ticker: string, start: string, end?: string) =>
  apiClient.get<OHLCVResponse>('/v1/data/ohlcv', {
    params: { ticker, start, end },
  }).then((r) => r.data)

export const fetchFundamentals = (ticker: string) =>
  apiClient.get<{ ticker: string; data: Record<string, unknown> }>('/v1/data/fundamentals', {
    params: { ticker },
  }).then((r) => r.data)

// ─── Quant endpoints ──────────────────────────────────────────────────────────

export interface FactorScore {
  name: string
  scores: Record<string, number>
  rank: Record<string, number>
}

export interface FactorResponse {
  universe: string
  factors: FactorScore[]
}

export const fetchFactors = (universe = 'ibovespa', factors = 'momentum_12_1') =>
  apiClient.get<FactorResponse>('/v1/factors', {
    params: { universe, factors },
  }).then((r) => r.data)

// ─── Health ───────────────────────────────────────────────────────────────────

export const fetchHealth = () =>
  apiClient.get<{ status: string }>('/health').then((r) => r.data)
