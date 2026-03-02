# BQUANT — Personal Quantitative Finance Platform

A local, open-source Bloomberg BQUANT-inspired platform for quantitative research, backtesting, portfolio optimization, and live market data analysis.

---

## Architecture

```
finance/
├── backend/          # FastAPI REST + WebSocket server
│   ├── api/          # Route handlers (data, quant, portfolio)
│   ├── core/         # Config, database, dependencies
│   ├── data/         # Data fetchers, ORM models
│   └── quant/        # Factor engine, backtester, optimizer
├── frontend/
│   └── dashboard/    # React + TypeScript dashboard (Vite)
├── notebooks/        # JupyterLab research notebooks
├── strategies/       # Pluggable trading strategy modules
├── mybquant/         # Notebook-friendly Python API
├── migrations/       # Alembic DB migrations
├── docker/           # Dockerfiles + Nginx config
├── tests/            # Pytest test suite
└── docker-compose.yml
```

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.115, Python 3.12, asyncpg |
| Database | PostgreSQL 16 + TimescaleDB (hypertables) |
| Cache/Queue | Redis 7, Celery |
| Data Sources | yfinance, OpenBB, pandas-datareader, ccxt, BCB |
| Quant Engine | pandas, numpy, scipy, scikit-learn, PyPortfolioOpt |
| Backtesting | Nautilus Trader |
| Frontend | React 18, TypeScript, Vite 6, TailwindCSS 4 |
| Charts | TradingView Lightweight Charts, Recharts |
| Notebooks | JupyterLab 4 |
| Validation | Pydantic v2, mypy, ruff |

## Quick Start

### Prerequisites

- Docker Desktop
- Python 3.12
- Node.js 20+

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 2. Start all services

```bash
make up
# or: docker compose up -d
```

Services started:
| Service | URL |
|---|---|
| API | http://localhost/api/v1/health |
| Dashboard | http://localhost |
| JupyterLab | http://localhost/jupyter |
| Swagger UI | http://localhost/api/docs |

### 3. Run database migrations

```bash
make migrate
```

### 4. Install Python deps locally (for notebooks / tests)

```bash
make install-dev
# equivalent to: pip install -r requirements.txt -r requirements-dev.txt
```

### 5. Open the research notebook

```bash
make jupyter
# or visit http://localhost/jupyter after make up
```

Open `notebooks/01_data_exploration.ipynb` for a guided walkthrough.

---

## Makefile Targets

```
make up              Start Docker stack
make down            Stop Docker stack
make logs            Tail logs
make migrate         Run Alembic migrations
make install-dev     Install all Python deps in .venv
make test            Run pytest unit tests
make lint            Ruff lint check
make format          Ruff auto-format
make type-check      mypy static analysis
make jupyter         Open JupyterLab in browser
make clean           Remove Docker volumes (destructive!)
```

## Python API (Notebooks)

```python
from mybquant import data, quant, portfolio

# Fetch price data
prices = data.get_prices(["PETR4.SA", "VALE3.SA", "ITUB4.SA"], start="2020-01-01")

# Compute cross-sectional factors
factors = quant.factors.compute(
    universe=["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    factors=["momentum_12_1", "low_vol_12"],
    start="2020-01-01",
)

# Run backtest
result = quant.backtest.run(
    strategy="momentum",
    tickers=["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    start="2021-01-01",
)
print(result.summary())

# Optimize portfolio
opt = portfolio.optimize(
    tickers=["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    method="max_sharpe",
    constraints={"max_weight": 0.4},
)
print(opt.weights)
```

## REST API

```
GET  /api/v1/data/ohlcv?ticker=PETR4.SA&start=2020-01-01
GET  /api/v1/data/fundamentals?ticker=VALE3.SA
GET  /api/v1/factors?universe=ibovespa&factors=momentum_12_1,low_vol_12
POST /api/v1/backtest
POST /api/v1/portfolio/optimize
GET  /api/v1/health
```

## Market Focus

**Primary: Brazil (B3)**
- Equities: `.SA` suffix tickers (PETR4.SA, VALE3.SA, ITUB4.SA, ...)
- Indices: IBOV, IFIX, SMLL, IDIV

**Secondary: US Markets**
- S&P 500, NASDAQ 100, sector ETFs (SPY, QQQ, IWM)

## Implementation Phases

- [x] **Phase 1 — Foundation**: Docker stack, data layer, FastAPI, quant engine, React dashboard, Jupyter notebooks
- [ ] **Phase 2 — Quant Core**: Full factor model, enhanced backtesting, risk analytics, pyfolio tearsheets
- [ ] **Phase 3 — Dashboard**: Complete UI, real-time WebSocket streaming, factor explorer, backtest viewer
- [ ] **Phase 4 — AI Copilot**: Ollama integration, LangChain pipelines, RAG on quant docs
- [ ] **Phase 5 — Production**: Auth (JWT), monitoring (Prometheus + Grafana), comprehensive test coverage

## License

MIT
