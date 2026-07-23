from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Sentiment settings
    max_batch_size: int = 32
    max_text_length: int = 512

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 256
    openai_max_reviews: int = 50

    # CORS
    cors_origins: str = "*"

    # App
    app_name: str = "Amazon Review Insights API"
    app_version: str = "1.0.0"
    debug: bool = False


settings = Settings()