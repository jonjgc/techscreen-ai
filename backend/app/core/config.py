from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "TechScreen AI"
    version: str = "0.1.0"
    environment: str = "development"
    secret_key: str = "dev-secret-key"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://techscreen:techscreen_pass@db:5432/techscreen_db"
    database_sync_url: Optional[str] = None

    # Redis / Celery
    redis_url: str = "redis://redis:6379/0"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    @property
    def celery_broker_url(self) -> str:
        return self.redis_url

    @property
    def celery_result_backend(self) -> str:
        return self.redis_url


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
