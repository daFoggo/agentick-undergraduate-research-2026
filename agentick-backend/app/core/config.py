from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentick Backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"
    debug: bool = True

    database_url: str = "postgresql+psycopg://agentick:agentick_local_dev@localhost:5432/agentick"

    internal_admin_token: str = "change-me"

    jwt_secret_key: str = "change-me-to-a-random-64-char-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: list[str] = ["http://localhost:3000"]

    # Environments where interactive docs (/docs, /redoc, /openapi.json) are served.
    # Anywhere else (e.g. "production") they're disabled by default to avoid
    # publicly exposing the schema.
    docs_enabled_environments: set[str] = {"local", "staging"}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def docs_enabled(self) -> bool:
        return self.environment in self.docs_enabled_environments


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
