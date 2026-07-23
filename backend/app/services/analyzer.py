from __future__ import annotations

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

Respond ONLY in this exact JSON format:

{{
  "label":"POSITIVE",
  "score":0.98
}}

Review:
{text}
"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response.choices[0].message.content

    import json

    result = json.loads(content)

    return {
        "label": result["label"],
        "score": round(float(result["score"]), 6),
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