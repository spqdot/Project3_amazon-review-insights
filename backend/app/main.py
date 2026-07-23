from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    HealthResponse,
    SentimentResult,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services import analyzer, summarizer

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up — preloading sentiment model…")
    analyzer.preload_pipeline()
    yield
    logger.info("Shutting down.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-ready NLP backend for Amazon review insights. "
        "Provides sentiment analysis and optional AI-powered summarization."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health_check() -> HealthResponse:
    """Return service status and basic metadata."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        model_name=settings.model_name,
        model_loaded=analyzer.is_model_loaded(),
    )


@app.post("/analyze", response_model=AnalyzeResponse, tags=["analysis"])
def analyze_single(body: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze the sentiment of a single review text.

    Returns the predicted **label** (e.g. `POSITIVE` / `NEGATIVE`) and the
    model's **confidence score**.
    """
    try:
        result = analyzer.analyze_text(body.text)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model unavailable: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during /analyze")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during analysis.",
        ) from exc

    return AnalyzeResponse(result=SentimentResult(**result))


@app.post("/analyze/batch", response_model=BatchAnalyzeResponse, tags=["analysis"])
def analyze_batch(body: BatchAnalyzeRequest) -> BatchAnalyzeResponse:
    """
    Analyze the sentiment of a batch of review texts (up to 32 at a time).

    Each item in the response corresponds positionally to the input list.
    """
    if len(body.texts) > settings.max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Batch size exceeds maximum of {settings.max_batch_size}.",
        )

    try:
        results = analyzer.analyze_batch(body.texts)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model unavailable: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during /analyze/batch")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch analysis.",
        ) from exc

    return BatchAnalyzeResponse(
        results=[SentimentResult(**r) for r in results],
        total=len(results),
    )


@app.post("/summarize", response_model=SummarizeResponse, tags=["summarization"])
def summarize_reviews(body: SummarizeRequest) -> SummarizeResponse:
    """
    Summarize a list of reviews.

    If `OPENAI_API_KEY` is set in the environment the endpoint uses the OpenAI
    Chat API; otherwise it falls back to a deterministic extractive summary.
    """
    try:
        result = summarizer.summarize(body.texts, max_sentences=body.max_sentences)
    except Exception as exc:
        logger.exception("Unexpected error during /summarize")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during summarization.",
        ) from exc

    return SummarizeResponse(**result)
