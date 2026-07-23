from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model settings
    model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"
    max_batch_size: int = 32
    max_text_length: int = 512
    # Internal batch size passed to the HuggingFace pipeline (tune for your hardware)
    pipeline_batch_size: int = 8
    # Maximum number of reviews sent to OpenAI for summarization (token-limit guard)
    openai_max_reviews: int = 50

    # Optional GenAI settings
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 256

    # CORS — comma-separated list of allowed origins.
    # Use "*" only for development; restrict to specific domains in production.
    cors_origins: str = "*"

    # App settings
    app_name: str = "Amazon Review Insights API"
    app_version: str = "1.0.0"
    debug: bool = False


settings = Settings()
