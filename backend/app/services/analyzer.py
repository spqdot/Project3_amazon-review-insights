from __future__ import annotations

import logging
from typing import Any

import requests

from ..config import settings

logger = logging.getLogger(__name__)

API_URL = (
    f"https://api-inference.huggingface.co/models/{settings.model_name}"
)

HEADERS = {
    "Authorization": f"Bearer {settings.hf_token}"
}


def is_model_loaded() -> bool:
    return True


def preload_pipeline() -> None:
    logger.info("Using Hugging Face Inference API.")


def _predict(text: str) -> dict[str, Any]:
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": text},
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    # Handle nested response format
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list):
            result = result[0]

    best = max(result, key=lambda x: x["score"])

    return {
        "label": best["label"],
        "score": round(float(best["score"]), 6),
        "text_snippet": text[:120] if len(text) > 120 else text,
    }


def analyze_text(text: str) -> dict[str, Any]:
    return _predict(text)


def analyze_batch(texts: list[str]) -> list[dict[str, Any]]:
    if len(texts) > settings.max_batch_size:
        raise ValueError(
            f"Batch size {len(texts)} exceeds maximum of {settings.max_batch_size}"
        )

    return [_predict(text) for text in texts]