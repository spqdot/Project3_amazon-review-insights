from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from ..config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)


def is_model_loaded() -> bool:
    return True


def preload_pipeline() -> None:
    logger.info("Using OpenAI for sentiment analysis.")


def _predict(text: str) -> dict[str, Any]:
    prompt = f"""
Analyze the sentiment of the following review.

Return ONLY valid JSON in exactly this format:

{{
    "label": "POSITIVE",
    "score": 0.98
}}

Review:
{text}
"""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis model. Return only JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()

        logger.info("OpenAI response: %s", content)

        result = json.loads(content)

        return {
            "label": result["label"],
            "score": float(result["score"]),
            "text_snippet": text[:120],
        }

    except Exception:
        logger.exception("OpenAI sentiment request failed")
        raise


def analyze_text(text: str) -> dict[str, Any]:
    return _predict(text)


def analyze_batch(texts: list[str]) -> list[dict[str, Any]]:
    if len(texts) > settings.max_batch_size:
        raise ValueError(
            f"Batch size {len(texts)} exceeds maximum of {settings.max_batch_size}"
        )

    return [_predict(text) for text in texts]