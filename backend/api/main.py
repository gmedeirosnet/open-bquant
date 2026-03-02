"""FastAPI application entrypoint for BQUANT backend."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.api.routers import data, quant, portfolio
from backend.core.config import settings
from backend.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Starting BQUANT backend...")
    # Create tables (dev mode — production uses Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified.")
    yield
    logger.info("Shutting down BQUANT backend...")
    await engine.dispose()


app = FastAPI(
    title="BQUANT API",
    description="Personal Bloomberg BQUANT replica — quantitative finance platform",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(quant.router, prefix="/api/v1", tags=["quant"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Liveness probe — returns 200 when the service is up."""
    return {"status": "ok", "service": "bquant-backend"}
