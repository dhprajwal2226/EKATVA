"""
app/core/config.py

Central application configuration using pydantic-settings.
All settings are read from environment variables / .env file.
"""
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_TITLE: str = "National Material Master Governance API"
    APP_VERSION: str = "1.0.0"

    # ── Database ───────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:changeme@localhost:5432/national_material_master"
    )
    SYNC_DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:changeme@localhost:5432/national_material_master"
    )

    # ── JWT ────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Security ───────────────────────────────────────────────────
    MIN_PASSWORD_LENGTH: int = 12

    # ── Rate Limiting ──────────────────────────────────────────────
    LOGIN_RATE_LIMIT: int = 5  # attempts per minute per IP

    # ── CORS ───────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ── First Admin (seed only) ────────────────────────────────────
    ADMIN_EMPLOYEE_ID: str = "ADMIN001"
    ADMIN_EMAIL: str = "admin@national-material-master.gov.in"
    ADMIN_PASSWORD: str = "CHANGE_ME_STRONG_PASSWORD_12chars"
    ADMIN_NAME: str = "System Administrator"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()


settings = get_settings()
