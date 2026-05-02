from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="whatsapp-ai-sales-agent", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_version: str = Field(default="0.2.0", alias="APP_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    agent_config_path: Path = Field(
        default=Path("data/agent_config.json"),
        alias="AGENT_CONFIG_PATH",
    )
    chroma_persist_dir: Path = Field(default=Path("chroma"), alias="CHROMA_PERSIST_DIR")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openai/gpt-4o-mini", alias="OPENROUTER_MODEL")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL",
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    evolution_api_url: str | None = Field(default=None, alias="EVOLUTION_API_URL")
    evolution_api_instance: str | None = Field(default=None, alias="EVOLUTION_API_INSTANCE")
    evolution_api_key: str | None = Field(default=None, alias="EVOLUTION_API_KEY")
    webhook_rate_limit: int = Field(default=20, alias="WEBHOOK_RATE_LIMIT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
