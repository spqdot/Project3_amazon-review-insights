# Amazon Review Insights

An NLP-powered backend that delivers **sentiment analysis** and **AI summarization** for Amazon product reviews, built with FastAPI and HuggingFace Transformers.

---

## Repository layout

```
.
├── backend/                  # FastAPI service (this README section)
│   ├── app/
│   │   ├── main.py           # FastAPI app & routes
│   │   ├── config.py         # Pydantic settings (env-var driven)
│   │   ├── schemas.py        # Request / response models
│   │   └── services/
│   │       ├── analyzer.py   # HuggingFace sentiment pipeline
│   │       └── summarizer.py # OpenAI / fallback summarizer
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── runtime.txt
│   └── .env.example
├── notebooks/                # Exploration & model-training notebooks
├── render.yaml               # Render.com service definition
└── README.md
```

---

## Backend — local development

### Prerequisites

- Python 3.11+
- (Recommended) a virtual environment

### 1. Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env — set MODEL_NAME, and optionally OPENAI_API_KEY
```

### 3. Start the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## API endpoints

### `GET /health`

Returns service status and model metadata.

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "app_name": "Amazon Review Insights API",
  "version": "1.0.0",
  "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
  "model_loaded": true
}
```

---

### `POST /analyze`

Analyze the sentiment of a single review.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is absolutely fantastic! Highly recommend."}'
```

Example response:

```json
{
  "result": {
    "label": "POSITIVE",
    "score": 0.999847,
    "text_snippet": "This product is absolutely fantastic! Highly recommend."
  }
}
```

---

### `POST /analyze/batch`

Analyze up to 32 reviews in a single request.

```bash
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great product, fast shipping!",
      "Broke after one week. Very disappointed.",
      "Decent quality for the price."
    ]
  }'
```

Example response:

```json
{
  "results": [
    {"label": "POSITIVE", "score": 0.9997, "text_snippet": "Great product, fast shipping!"},
    {"label": "NEGATIVE", "score": 0.9985, "text_snippet": "Broke after one week. Very disappointed."},
    {"label": "POSITIVE", "score": 0.8741, "text_snippet": "Decent quality for the price."}
  ],
  "total": 3
}
```

---

### `POST /summarize`

Summarize a list of reviews.  
Uses the **OpenAI Chat API** when `OPENAI_API_KEY` is set; otherwise falls back to a deterministic extractive summary.

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great product, fast shipping!",
      "Broke after one week. Very disappointed.",
      "Decent quality for the price."
    ],
    "max_sentences": 2
  }'
```

Example response (fallback mode):

```json
{
  "summary": "Great product, fast shipping! Broke after one week.",
  "method": "fallback"
}
```

---

## Deploying to Render.com

### Option A — One-click via `render.yaml` (recommended)

1. Fork / push this repository to your GitHub account.
2. Go to [https://dashboard.render.com](https://dashboard.render.com) and click **New → Blueprint**.
3. Select your repository.  Render will detect `render.yaml` and create the service automatically.
4. Set the `OPENAI_API_KEY` secret in the Render dashboard under **Environment → Secret Files** (optional).
5. Click **Apply** — Render builds the Docker image and deploys.

### Option B — Manual web service

1. In the Render dashboard click **New → Web Service**.
2. Connect your repository.
3. Choose **Docker** as the runtime.
4. Set:
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Build Context**: `backend`
5. Add environment variables (see `.env.example` for the full list).
6. Set the **Health Check Path** to `/health`.
7. Click **Create Web Service**.

### Environment variable reference

| Variable | Default | Required | Description |
|---|---|---|---|
| `MODEL_NAME` | `distilbert-base-uncased-finetuned-sst-2-english` | No | HuggingFace model for sentiment analysis |
| `MAX_BATCH_SIZE` | `32` | No | Max reviews per `/analyze/batch` request |
| `MAX_TEXT_LENGTH` | `512` | No | Token truncation limit |
| `OPENAI_API_KEY` | _(empty)_ | No | Enables AI-powered `/summarize` |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | No | OpenAI model used for summarization |
| `OPENAI_MAX_TOKENS` | `256` | No | Max tokens in OpenAI summary response |
| `DEBUG` | `false` | No | Enable verbose logging |

---

## Notebooks

The `notebooks/` directory contains the original exploration and model-training work:

| Notebook | Description |
|---|---|
| `01_Preprocessing.ipynb` | Data cleaning and text preprocessing |
| `02_EDA.ipynb` | Exploratory data analysis |
| `03_sentiment_analysis/` | Multiple model experiments (TF-IDF, BERT, etc.) |
| `04_Clustering.ipynb` | Review clustering |
| `05_Summarization/` | Summarization model comparisons (DistilBART, T5, OpenAI) |

The backend service is independent of notebook outputs — it downloads model weights from HuggingFace Hub at startup.

---

## Quick verification

After deploying (or running locally) run the health check:

```bash
curl https://<your-service>.onrender.com/health
```

Expected output:

```json
{"status": "ok", "model_loaded": true, ...}
```

Then send a test review:

```bash
curl -X POST https://<your-service>.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Amazing quality, will buy again!"}'
```

---

## Assumptions & notes

- **Model weights** are downloaded from HuggingFace Hub on first startup.  The default model (`distilbert-base-uncased-finetuned-sst-2-english`) is ~260 MB; first cold start on Render may take 2–3 minutes.
- **Notebook-trained models** — if you export a fine-tuned model from the notebooks, set `MODEL_NAME` to the local path (e.g. `./models/my-bert`) and mount it in the Docker image.
- **OpenAI key** is entirely optional; all endpoints work without it.
- The service uses CPU inference by default.  For GPU, update the Render plan and set `device=0` in `analyzer.py`.