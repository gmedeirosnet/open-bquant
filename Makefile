# ─────────────────────────────────────────────────────────────────────────────
# BQUANT — Makefile
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help up down restart logs ps build \
        migrate migrate-create db-shell redis-shell \
        install install-dev test lint format type-check \
        jupyter clean

PYTHON  = .venv/bin/python
PIP     = .venv/bin/pip
PYTEST  = .venv/bin/pytest
RUFF    = .venv/bin/ruff
MYPY    = .venv/bin/mypy

# ─────────────────────────────────────────────────────────────────────────────
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────

up: .env  ## Start all services (Docker Compose)
	docker compose up -d
	@echo "✓ Services started. Dashboard: http://localhost  JupyterLab: http://localhost/jupyter"

down:  ## Stop all services
	docker compose down

restart:  ## Restart all services
	docker compose restart

logs:  ## Tail logs from all services
	docker compose logs -f

ps:  ## Show service status
	docker compose ps

build:  ## Force rebuild all Docker images
	docker compose build --no-cache

# ─────────────────────────────────────────────────────────────────────────────
# Database / Migrations
# ─────────────────────────────────────────────────────────────────────────────

migrate: .env  ## Apply all pending migrations
	$(PYTHON) -m alembic upgrade head

migrate-create:  ## Create a new migration (usage: make migrate-create MSG="description")
	$(PYTHON) -m alembic revision --autogenerate -m "$(MSG)"

db-shell:  ## Connect to PostgreSQL shell
	docker compose exec db psql -U $${POSTGRES_USER:-bquant} -d $${POSTGRES_DB:-bquant}

redis-shell:  ## Connect to Redis CLI
	docker compose exec redis redis-cli

# ─────────────────────────────────────────────────────────────────────────────
# Python Environment
# ─────────────────────────────────────────────────────────────────────────────

.env:  ## Create .env from template if not exists
	@test -f .env || (cp .env.example .env && echo "⚠  Created .env from .env.example — edit before running.")

install: .venv  ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e . --no-build-isolation 2>/dev/null || true

install-dev: install  ## Install all dependencies including dev tools
	$(PIP) install -r requirements-dev.txt
	$(PIP) install jupyterlab ipywidgets matplotlib plotly nest_asyncio

.venv:
	python3.12 -m venv .venv

# ─────────────────────────────────────────────────────────────────────────────
# Quality
# ─────────────────────────────────────────────────────────────────────────────

test:  ## Run test suite
	$(PYTEST) tests/ -v --tb=short

lint:  ## Run ruff linter
	$(RUFF) check .

format:  ## Auto-format code with ruff
	$(RUFF) format .

type-check:  ## Run mypy type checker
	$(MYPY) backend/ mybquant/ strategies/ --ignore-missing-imports

# ─────────────────────────────────────────────────────────────────────────────
# Jupyter
# ─────────────────────────────────────────────────────────────────────────────

jupyter:  ## Open JupyterLab in browser (local, not Docker)
	$(PYTHON) -m jupyter lab --notebook-dir=notebooks --port=8889

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────

clean:  ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleaned up caches."
