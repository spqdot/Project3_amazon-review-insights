# -----------------------------------------------------------------------
# Multi-stage Dockerfile for Amazon Review Insights — Backend
# Optimised for Render.com Web Service deployments.
# -----------------------------------------------------------------------

# ---- Build stage -------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install into a prefix that we can copy into the runtime image
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# ---- Runtime stage ------------------------------------------------------
FROM python:3.11-slim

# Create a non-root user for security
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
USER appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/

# Expose the port Render will bind to (injected via $PORT at runtime)
EXPOSE 8000

# Start the ASGI server.  Render injects $PORT; fall back to 8000.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
