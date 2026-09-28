"""
Centralized Configuration for Core AI Material Intelligence Engine.
SIH 2026 - National Material Master Platform for CPSEs.
"""

from typing import List, Optional
import os

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field

    class Settings(BaseSettings):
        PROJECT_NAME: str = "National Material Master AI Engine"
        VERSION: str = "1.0.0"
        API_V1_STR: str = "/api"

        # Database Configuration
        DATABASE_URL: str = Field(
            default="sqlite:///./ekatva_materials.db",
            description="Database connection string (PostgreSQL with pgvector in production, SQLite fallback)",
        )
        DB_ECHO: bool = False

        # Decision support / analytics settings (from decision-support branch)
        APP_ENV: str = "development"
        LOG_LEVEL: str = "INFO"
        JWT_SECRET: str = "secret"
        LLM_API_KEY: Optional[str] = None
        LLM_MODEL: str = "gemini-1.5-pro"

        # Hybrid Matching Weights
        SEMANTIC_WEIGHT: float = Field(default=0.30, description="Weight for vector semantic similarity (0.0 - 1.0)")
        FUZZY_WEIGHT: float = Field(default=0.20, description="Weight for lexical fuzzy similarity (0.0 - 1.0)")
        ATTRIBUTE_WEIGHT: float = Field(default=0.30, description="Weight for structured attribute similarity (0.0 - 1.0)")
        TECHNICAL_WEIGHT: float = Field(default=0.20, description="Weight for technical rule compliance (0.0 - 1.0)")

        # Candidate Generation
        CANDIDATE_TOP_K: int = Field(default=25, description="Number of candidate records retrieved for detailed comparison")
        MIN_CANDIDATE_SCORE: float = Field(default=0.35, description="Minimum pre-filter similarity score for candidates")

        # Classification Thresholds
        IDENTICAL_THRESHOLD: float = Field(default=0.94, description="Minimum score for IDENTICAL match when no conflicts exist")
        NEAR_DUPLICATE_THRESHOLD: float = Field(default=0.82, description="Score threshold for NEAR_DUPLICATE classification")
        FUNCTIONAL_EQUIVALENT_THRESHOLD: float = Field(default=0.72, description="Score threshold for FUNCTIONALLY_EQUIVALENT")
        REVIEW_THRESHOLD: float = Field(default=0.60, description="Score threshold below which materials are DIFFERENT")

        # Technical Conflict Behavior
        CRITICAL_CONFLICT_BEHAVIOR: str = Field(
            default="DO_NOT_AUTO_MERGE",
            description="Enforced action when critical technical conflict is detected"
        )

        # AI & Embeddings
        EMBEDDING_MODEL: str = Field(
            default="all-MiniLM-L6-v2",
            description="SentenceTransformer embedding model name"
        )
        EMBEDDING_DIMENSION: int = 384

        # File Ingestion Security
        MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
        ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
        ALLOWED_MIME_TYPES: List[str] = [
            "text/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "application/octet-stream",
        ]

        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": True,
            "extra": "ignore",
        }

except ImportError:
    # Standard Python fallback without pydantic-settings installed
    class Settings:  # type: ignore
        PROJECT_NAME: str = "National Material Master AI Engine"
        VERSION: str = "1.0.0"
        API_V1_STR: str = "/api"

        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ekatva_materials.db")
        DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

        APP_ENV: str = os.getenv("APP_ENV", "development")
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        JWT_SECRET: str = os.getenv("JWT_SECRET", "secret")
        LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
        LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-pro")

        SEMANTIC_WEIGHT: float = float(os.getenv("SEMANTIC_WEIGHT", "0.30"))
        FUZZY_WEIGHT: float = float(os.getenv("FUZZY_WEIGHT", "0.20"))
        ATTRIBUTE_WEIGHT: float = float(os.getenv("ATTRIBUTE_WEIGHT", "0.30"))
        TECHNICAL_WEIGHT: float = float(os.getenv("TECHNICAL_WEIGHT", "0.20"))

        CANDIDATE_TOP_K: int = int(os.getenv("CANDIDATE_TOP_K", "25"))
        MIN_CANDIDATE_SCORE: float = float(os.getenv("MIN_CANDIDATE_SCORE", "0.35"))

        IDENTICAL_THRESHOLD: float = float(os.getenv("IDENTICAL_THRESHOLD", "0.94"))
        NEAR_DUPLICATE_THRESHOLD: float = float(os.getenv("NEAR_DUPLICATE_THRESHOLD", "0.82"))
        FUNCTIONAL_EQUIVALENT_THRESHOLD: float = float(os.getenv("FUNCTIONAL_EQUIVALENT_THRESHOLD", "0.72"))
        REVIEW_THRESHOLD: float = float(os.getenv("REVIEW_THRESHOLD", "0.60"))

        CRITICAL_CONFLICT_BEHAVIOR: str = os.getenv("CRITICAL_CONFLICT_BEHAVIOR", "DO_NOT_AUTO_MERGE")
        EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        EMBEDDING_DIMENSION: int = 384

        MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024
        ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
        ALLOWED_MIME_TYPES: List[str] = [
            "text/csv",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "application/octet-stream",
        ]


settings = Settings()
