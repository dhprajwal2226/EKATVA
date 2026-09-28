"""
Database Engine, Session Management, and Base Definition.
Supports PostgreSQL (with pgvector in production) and SQLite (for lightweight testing).
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Construct engine based on DATABASE_URL
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args=connect_args,
    pool_pre_ping=True if "sqlite" not in settings.DATABASE_URL else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """Dependency injection helper for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
