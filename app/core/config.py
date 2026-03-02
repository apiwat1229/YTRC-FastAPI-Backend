from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        enable_decoding=False,
    )

    database_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 2530
    api_prefix: str = "/api"

    jwt_secret: str = "your-secret-key"
    jwt_expiration: str = "7d"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8888", "http://localhost:5173"]
    environment: str = "development"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return value
        return []


settings = Settings()
