from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "National Material Intelligence Engine"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/national_intelligence"

settings = Settings()
