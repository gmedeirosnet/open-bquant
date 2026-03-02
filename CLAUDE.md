# CLAUDE.md — Personal BQUANT Platform

## 🎯 Project Vision

Build a **personal quantitative finance platform** inspired by Bloomberg BQUANT, combining:
- JupyterHub environment for interactive analysis
- Real-time and historical market data ingestion
- Quantitative research tools (backtesting, factor models, risk)
- A modern web dashboard for visualization
- Local LLM integration for AI-assisted analysis

The platform must be **fully local, open-source, and production-grade**.

---

## 🏗️ Architecture Overview

```
my-bquant/
├── backend/
│   ├── api/              # FastAPI REST + WebSocket server
│   ├── data/             # Data ingestion & storage layer
│   ├── quant/            # Quantitative engines
│   └── ai/               # LLM integration (Ollama)
├── frontend/
│   ├── dashboard/        # React dashboard (charts, widgets)
│   └── notebook/         # JupyterLab interface
├── notebooks/            # Research notebooks (.ipynb)
├── strategies/           # Trading strategy modules
├── data/
│   ├── raw/              # Raw market data
│   ├── processed/        # Cleaned/normalized data
│   └── cache/            # Redis cache layer
├── docker/               # Docker Compose setup
├── tests/
└── CLAUDE.md
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** — primary language
- **FastAPI** — REST API + WebSocket server
- **Celery + Redis** — async task queue for data pipelines
- **PostgreSQL + TimescaleDB** — time-series financial data storage
- **SQLAlchemy** — ORM for relational data

### Data Sources (free/open)
- `yfinance` — Yahoo Finance (equities, ETFs, FX, crypto)
- `openbb` (OpenBB SDK) — multi-source financial data
- `pandas-datareader` — FRED, World Bank, Quandl
- `ccxt` — crypto exchanges
- `alpha_vantage` — fundamentals (free tier API)
- `bcb` — Banco Central do Brasil (for Brazilian markets)

### Quantitative Engine
- `pandas`, `numpy` — data manipulation
- `scipy`, `statsmodels` — statistical models
- `scikit-learn` — machine learning
- `vectorbt` — backtesting engine (vectorized, fast)
- `QuantLib` — derivatives pricing
- `pyfolio` / `empyrical` — portfolio analytics
- `PyPortfolioOpt` — portfolio optimization

### Frontend
- **React + TypeScript** — dashboard UI
- **TradingView Lightweight Charts** — candlestick/time-series charts
- **Recharts / Plotly.js** — analytical charts
- **Tailwind CSS** — styling
- **JupyterLab** — notebook interface

### AI Layer
- **Ollama** — local LLM runtime
  - Recommended models: `deepseek-coder`, `llama3`, `codellama`
- **LangChain** — LLM orchestration
- Custom finance-aware prompts for code generation and analysis

### Infrastructure
- **Docker + Docker Compose** — containerized deployment
- **Redis** — caching + message broker
- **Nginx** — reverse proxy

---

## 📋 Core Modules to Build

### 1. Data Layer (`backend/data/`)

```python
# Responsibilities:
# - Unified data fetcher (abstract over multiple sources)
# - Automatic caching with Redis (TTL per asset type)
# - Historical data storage in TimescaleDB
# - Real-time streaming via WebSocket
# - Corporate actions adjustment (splits, dividends)
```

**Key classes:**
- `DataFetcher` — unified interface for all data sources
- `MarketDataStore` — TimescaleDB read/write
- `DataPipeline` — Celery tasks for scheduled ingestion
- `UniverseManager` — define and manage asset universes

### 2. Quantitative Engine (`backend/quant/`)

```python
# Responsibilities:
# - Factor computation (momentum, value, quality, low-vol)
# - Portfolio construction and optimization
# - Backtesting engine wrapper
# - Risk analytics (VaR, CVaR, drawdown, attribution)
# - Statistical arbitrage tools
```

**Key classes:**
- `FactorEngine` — compute and rank factors cross-sectionally
- `Backtester` — strategy simulation with realistic costs
- `RiskAnalyzer` — risk metrics and stress testing
- `PortfolioOptimizer` — mean-variance, Black-Litterman, risk parity

### 3. Strategy Framework (`strategies/`)

```python
# Every strategy must implement the BaseStrategy interface:

class BaseStrategy(ABC):
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series: ...

    @abstractmethod
    def size_positions(self, signals: pd.Series) -> pd.Series: ...

    @abstractmethod
    def get_parameters(self) -> dict: ...
```

### 4. API Server (`backend/api/`)

```
GET  /api/v1/data/ohlcv?ticker=PETR4.SA&start=2020-01-01&end=today
GET  /api/v1/data/fundamentals?ticker=VALE3.SA
GET  /api/v1/factors?universe=ibovespa&factors=momentum,value
POST /api/v1/backtest          # Run backtest
GET  /api/v1/backtest/{id}     # Get results
POST /api/v1/portfolio/optimize
GET  /api/v1/risk/metrics?portfolio_id=...
WS   /ws/market-data           # Real-time streaming
POST /api/v1/ai/analyze        # LLM-powered analysis
POST /api/v1/ai/generate-code  # LLM code generation
```

### 5. Dashboard (`frontend/dashboard/`)

**Pages/Widgets to build:**
- `MarketOverview` — index heatmaps, movers
- `StockChart` — candlestick + technical indicators overlay
- `FactorExplorer` — factor returns, IC, turnover
- `BacktestViewer` — equity curve, drawdown, metrics table
- `PortfolioAnalyzer` — weights, attribution, risk decomposition
- `ScreenerTable` — filterable asset screener with factor scores
- `AICopilot` — chat interface with local LLM

### 6. AI Copilot (`backend/ai/`)

```python
# Capabilities:
# - Explain financial data/charts in natural language
# - Generate Python analysis code from natural language prompts
# - Summarize backtest results
# - Suggest strategy improvements
# - Answer quant finance questions using RAG on local docs
```

---

## 🔧 Development Guidelines

### Code Standards
- Use **type hints** everywhere
- **Pydantic v2** for all data models and validation
- **async/await** for all I/O operations (FastAPI + asyncpg)
- Write **unit tests** for all quantitative functions (pytest)
- Use **loguru** for structured logging
- Follow **PEP 8** with `ruff` as linter

### Data Conventions
```python
# OHLCV DataFrame schema (always enforce this):
# index: DatetimeIndex (UTC, business days only)
# columns: open, high, low, close, volume, adj_close
# ticker stored as metadata or in MultiIndex

# Returns always as log returns unless specified:
log_returns = np.log(prices / prices.shift(1))
```

### Financial Conventions
- Prices always **adjusted for corporate actions**
- Returns computed on **adjusted close**
- Backtest must account for: slippage, commissions, short borrow costs
- Risk metrics use **252 trading days/year** (Brazilian: 252, US: 252)
- All datetimes in **UTC**, display in local timezone

### Performance Requirements
- OHLCV data fetch < 200ms (from cache)
- Backtest on 5yr daily data for 100 assets < 5s
- Factor computation for Ibovespa universe < 10s
- Dashboard initial load < 2s

---

## 🚀 Implementation Phases

### Phase 1 — Foundation (Week 1-2)
- [ ] Docker Compose setup (PostgreSQL/TimescaleDB, Redis, JupyterLab)
- [ ] Data fetcher with yfinance + OpenBB
- [ ] TimescaleDB schema + migrations (Alembic)
- [ ] FastAPI skeleton with health checks
- [ ] Basic OHLCV endpoints

### Phase 2 — Quant Core (Week 3-4)
- [ ] Factor engine (momentum, value, quality, low-vol)
- [ ] Backtesting integration with vectorbt
- [ ] Risk metrics module
- [ ] Portfolio optimizer
- [ ] Jupyter notebooks for research workflow

### Phase 3 — Dashboard (Week 5-6)
- [ ] React project setup + routing
- [ ] TradingView chart component
- [ ] Market overview page
- [ ] Backtest results viewer
- [ ] Factor explorer

### Phase 4 — AI Copilot (Week 7-8)
- [ ] Ollama integration
- [ ] LangChain pipeline for code generation
- [ ] Chat interface in dashboard
- [ ] RAG on quantitative finance documentation

### Phase 5 — Production Hardening
- [ ] Authentication (JWT)
- [ ] Rate limiting
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Comprehensive test suite
- [ ] Documentation

---

## 📁 Key Files to Create First

When starting, create these files in order:

1. `docker-compose.yml` — full infrastructure stack
2. `backend/data/fetcher.py` — unified data interface
3. `backend/data/models.py` — Pydantic + SQLAlchemy models
4. `backend/api/main.py` — FastAPI app entrypoint
5. `backend/quant/factors.py` — factor computation engine
6. `backend/quant/backtester.py` — backtesting wrapper
7. `frontend/src/App.tsx` — React dashboard entrypoint
8. `notebooks/01_data_exploration.ipynb` — starter research notebook

---

## 🌎 Market Focus

### Primary: Brazil (B3)
- Equities: tickers with `.SA` suffix (PETR4.SA, VALE3.SA)
- Indices: IBOV, IFIX, SMLL, IDIV
- Fixed Income: Tesouro Direto, CDI, IPCA+
- FX: BRL/USD

### Secondary: US Markets
- S&P 500, NASDAQ 100 constituents
- ETFs (SPY, QQQ, IWM)
- Sector ETFs

---

## 🧪 Example Usage (Target Developer Experience)

```python
# In a Jupyter notebook — this is the UX to aim for:

from mybquant import data, quant, portfolio

# 1. Fetch data
prices = data.get_prices(["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
                          start="2020-01-01")

# 2. Compute factors
factors = quant.factors.compute(
    universe="ibovespa",
    factors=["momentum_12_1", "value_ep", "quality_roe"],
    date="2024-01-01"
)

# 3. Run backtest
results = quant.backtest.run(
    strategy="long_short_factor",
    params={"factor": "momentum_12_1", "n_long": 10, "n_short": 10},
    start="2018-01-01",
    end="2024-01-01"
)

# 4. Analyze results
results.plot_equity_curve()
results.metrics  # Sharpe, Sortino, MaxDD, CAGR...

# 5. Optimize portfolio
opt = portfolio.optimize(
    expected_returns=factors["momentum_12_1"],
    method="max_sharpe",
    constraints={"max_weight": 0.1, "min_weight": 0.0}
)
```

---

## ⚠️ Important Constraints

- **No Bloomberg dependency** — use only open/free data sources
- **No cloud required** — everything runs locally via Docker
- **Privacy first** — no data sent to external APIs by default (except fetching market data)
- **LLM runs locally** via Ollama — no OpenAI/Anthropic API keys needed
- **Modular** — each module must work independently
- Keep **notebook-first** philosophy: all features accessible from Jupyter

---

## 📚 Reference Resources

- OpenBB SDK docs: https://docs.openbb.co
- vectorbt docs: https://vectorbt.dev
- PyPortfolioOpt: https://pyportfolioopt.readthedocs.io
- QuantLib Python: https://quantlib-python-docs.readthedocs.io
- TradingView Lightweight Charts: https://tradingview.github.io/lightweight-charts/
- Ollama: https://ollama.com/docs
