from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentick Backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"
    debug: bool = True

    database_url: str = "postgresql+psycopg://agentick:agentick_local_dev@localhost:5432/agentick"

    internal_admin_token: str = "change-me"

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
