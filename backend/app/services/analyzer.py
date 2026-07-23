from __future__ import annotations

import logging
from typing import Any

from huggingface_hub import InferenceClient

from ..config import settings

logger = logging.getLogger(__name__)

client = InferenceClient(
    api_key=settings.hf_token
)


def is_model_loaded() -> bool:
    """
    No local model is loaded.
    """
    return True


def preload_pipeline() -> None:
    """
    Nothing to preload.
    """
    logger.info("Using Hugging Face Inference API.")


def analyze_text(text: str) -> dict[str, Any]:
    """
    Analyze one review.
    """

    result = client.text_classification(
        text=text,
        model=settings.model_name,
    )

    return {
        "label": result.label,
        "score": round(float(result.score), 6),
        "text_snippet": text[:120] if len(text) > 120 else text,
    }


def analyze_batch(texts: list[str]) -> list[dict[str, Any]]:
    """
    Analyze multiple reviews.
    """

    if len(texts) > settings.max_batch_size:
        raise ValueError(
            f"Batch size {len(texts)} exceeds maximum of {settings.max_batch_size}"
        )

    output = []

    for text in texts:
        result = client.text_classification(
            text=text,
            model=settings.model_name,
        )

        output.append(
            {
                "label": result.label,
                "score": round(float(result.score), 6),
                "text_snippet": text[:120] if len(text) > 120 else text,
            }
        )

    return output