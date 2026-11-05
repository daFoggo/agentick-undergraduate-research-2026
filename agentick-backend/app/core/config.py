from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentick Backend"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"
    debug: bool = True

    database_url: str = "postgresql+psycopg://agentick:agentick_local_dev@localhost:11031/agentick"

    # Plane is the main system; this backend is an external service next to it. It calls Plane with
    # the bot's API key and learns who a caller is from their Plane session (no accounts here).
    plane_base_url: str = "http://localhost:31080"
    plane_api_key: SecretStr = SecretStr("")  # the bot user's token, used for writes only
    plane_workspace_slug: str = "ript"
    ingest_token: SecretStr = SecretStr(
        ""
    )  # bearer token of the offline job that publishes alerts and cases

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
