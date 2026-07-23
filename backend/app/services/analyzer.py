from __future__ import annotations

import logging
from typing import Any

from ..config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-loaded pipeline singleton
# ---------------------------------------------------------------------------

_pipeline: Any = None


def _load_pipeline() -> Any:
    """Load and cache the HuggingFace sentiment-analysis pipeline."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    try:
        from transformers import pipeline  # type: ignore

        logger.info("Loading sentiment pipeline: %s", settings.model_name)
        _pipeline = pipeline(
            "sentiment-analysis",
            model=settings.model_name,
            truncation=True,
            max_length=settings.max_text_length,
        )
        logger.info("Sentiment pipeline loaded successfully.")
    except Exception as exc:
        logger.error("Failed to load sentiment pipeline: %s", exc)
        raise RuntimeError(f"Could not load model '{settings.model_name}': {exc}") from exc

    return _pipeline


def is_model_loaded() -> bool:
    """Return True if the pipeline has already been loaded."""
    return _pipeline is not None


def preload_pipeline() -> None:
    """Eagerly load the pipeline (called at startup)."""
    try:
        _load_pipeline()
    except RuntimeError as exc:
        logger.warning("Startup model preload failed (will retry on first request): %s", exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_text(text: str) -> dict[str, Any]:
    """
    Run sentiment analysis on a single text.

    Returns a dict with keys: ``label``, ``score``, ``text_snippet``.
    """
    pipe = _load_pipeline()
    result: list[dict[str, Any]] = pipe(text, truncation=True, max_length=settings.max_text_length)
    item = result[0]
    return {
        "label": item["label"],
        "score": round(float(item["score"]), 6),
        "text_snippet": text[:120] if len(text) > 120 else text,
    }


def analyze_batch(texts: list[str]) -> list[dict[str, Any]]:
    """
    Run sentiment analysis on a batch of texts.

    Returns a list of dicts with keys: ``label``, ``score``, ``text_snippet``.
    """
    if len(texts) > settings.max_batch_size:
        raise ValueError(
            f"Batch size {len(texts)} exceeds maximum of {settings.max_batch_size}"
        )

    pipe = _load_pipeline()
    results: list[dict[str, Any]] = pipe(
        texts,
        truncation=True,
        max_length=settings.max_text_length,
        batch_size=min(len(texts), settings.pipeline_batch_size),
    )
    return [
        {
            "label": r["label"],
            "score": round(float(r["score"]), 6),
            "text_snippet": t[:120] if len(t) > 120 else t,
        }
        for r, t in zip(results, texts)
    ]
