"""Application configuration via pydantic-settings (reads from .env)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:80"],
    )

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://bquant:bquant_secret@localhost:5432/bquant"
    DATABASE_URL_SYNC: str = "postgresql://bquant:bquant_secret@localhost:5432/bquant"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── External APIs ──
    ALPHA_VANTAGE_API_KEY: str = "demo"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
