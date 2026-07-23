from __future__ import annotations

import logging
import re

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fallback_summary(texts: list[str], max_sentences: int = 3) -> str:
    """
    Deterministic extractive summary: return the first *max_sentences* unique
    sentences that together give the broadest coverage.
    """
    # Split every review into sentences (rough split on . ! ?)
    sentences: list[str] = []
    for text in texts:
        for s in re.split(r"(?<=[.!?])\s+", text):
            s = s.strip()
            if s and s not in sentences:
                sentences.append(s)

    if not sentences:
        return "No reviews provided."

    chosen = sentences[:max_sentences]
    summary = " ".join(chosen)
    return summary


def _openai_summary(texts: list[str], max_sentences: int = 3) -> str:
    """
    Generate a concise summary using the OpenAI Chat API.

    Raises ``RuntimeError`` when the API call fails so the caller can fall back
    to the deterministic path.
    """
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError("openai package is not installed") from exc

    client = OpenAI(api_key=settings.openai_api_key)
    joined = "\n---\n".join(texts[:50])  # cap at 50 reviews to stay within token limits
    prompt = (
        f"You are a helpful assistant. Summarize the following Amazon product reviews "
        f"in {max_sentences} concise sentences, highlighting the most common sentiments "
        f"and key themes.\n\nReviews:\n{joined}\n\nSummary:"
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=settings.openai_max_tokens,
        temperature=0.3,
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("OpenAI returned an empty response (content was None)")
    return content.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def summarize(texts: list[str], max_sentences: int = 3) -> dict[str, str]:
    """
    Summarize a list of review texts.

    Strategy (in priority order):
    1. OpenAI API — if ``OPENAI_API_KEY`` is configured.
    2. Deterministic extractive fallback — always available.

    Returns a dict with keys ``summary`` and ``method``.
    """
    if settings.openai_api_key:
        try:
            summary = _openai_summary(texts, max_sentences)
            return {"summary": summary, "method": "openai"}
        except Exception as exc:
            logger.warning("OpenAI summarization failed, falling back: %s", exc)

    summary = _fallback_summary(texts, max_sentences)
    return {"summary": summary, "method": "fallback"}
