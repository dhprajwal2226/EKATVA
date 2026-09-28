from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./national_materials.db" # Mock DB for demo
    JWT_SECRET: str = "secret" # From Person 2
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-pro"

    class Config:
        env_file = ".env"

settings = Settings()
