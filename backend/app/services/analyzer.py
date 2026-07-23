from __future__ import annotations

import logging
from typing import Any

from transformers import pipeline

from ..config import settings

logger = logging.getLogger(__name__)

classifier = pipeline(
    "sentiment-analysis",
    model=settings.model_name,
    framework="pt",
)

def is_model_loaded() -> bool:
    return classifier is not None

def preload_pipeline() -> None:
    logger.info("Loading sentiment model...")
    classifier("Model warmup")
    logger.info("Model loaded.")

def analyze_text(text: str) -> dict[str, Any]:
    result = classifier(text)[0]

    return {
        "label": result["label"],
        "score": round(float(result["score"]), 6),
        "text_snippet": text[:120] if len(text) > 120 else text,
    }

def analyze_batch(texts: list[str]) -> list[dict[str, Any]]:
    if len(texts) > settings.max_batch_size:
        raise ValueError(
            f"Batch size {len(texts)} exceeds maximum of {settings.max_batch_size}"
        )

    results = classifier(texts)

    output = []
    for text, result in zip(texts, results):
        output.append(
            {
                "label": result["label"],
                "score": round(float(result["score"]), 6),
                "text_snippet": text[:120] if len(text) > 120 else text,
            }
        )

    return output