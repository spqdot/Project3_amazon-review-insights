from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    text: str = Field(..., min_length=1, max_length=5000, description="Review text to analyze")

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be blank or whitespace-only")
        return v.strip()


class BatchAnalyzeRequest(BaseModel):
    """Request body for POST /analyze/batch."""

    texts: list[str] = Field(
        ...,
        min_length=1,
        max_length=32,
        description="List of review texts (max 32 per request)",
    )

    @field_validator("texts")
    @classmethod
    def texts_must_not_be_empty(cls, v: list[str]) -> list[str]:
        cleaned: list[str] = []
        for i, text in enumerate(v):
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"texts[{i}] must be a non-blank string")
            cleaned.append(text.strip())
        return cleaned


class SummarizeRequest(BaseModel):
    """Request body for POST /summarize."""

    texts: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of review texts (or analysis snippets) to summarize",
    )
    max_sentences: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Target number of sentences for the fallback summary",
    )

    @field_validator("texts")
    @classmethod
    def texts_must_not_be_empty(cls, v: list[str]) -> list[str]:
        cleaned: list[str] = []
        for i, text in enumerate(v):
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"texts[{i}] must be a non-blank string")
            cleaned.append(text.strip())
        return cleaned


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class SentimentResult(BaseModel):
    """Sentiment analysis result for a single review."""

    label: str = Field(..., description="Predicted sentiment label (e.g. POSITIVE, NEGATIVE)")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the label")
    text_snippet: Optional[str] = Field(
        default=None, description="First 120 characters of the input text"
    )


class AnalyzeResponse(BaseModel):
    """Response body for POST /analyze."""

    result: SentimentResult


class BatchAnalyzeResponse(BaseModel):
    """Response body for POST /analyze/batch."""

    results: list[SentimentResult]
    total: int = Field(..., description="Total number of texts processed")


class SummarizeResponse(BaseModel):
    """Response body for POST /summarize."""

    summary: str = Field(..., description="Generated or fallback summary")
    method: str = Field(
        ..., description="Method used: 'openai', 'transformers', or 'fallback'"
    )


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str = "ok"
    app_name: str
    version: str
    model_name: str
    model_loaded: bool
