from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads from .env by default; ignores unknown env vars to keep deploy flexible.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_timezone: str = "Asia/Jerusalem"
    log_level: str = "INFO"

    # Optional: can be useful for reference/logging; not required by FastAPI itself.
    api_port: int = 8001
    db_port: int = 5435

    database_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None
    telegram_webhook_path: str = "/api/v1/telegram/webhook"

    # Comma-separated list. Example: "http://localhost:5173,http://127.0.0.1:5173"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return origins


settings = Settings()
