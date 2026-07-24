# Amazon Review Insights

Amazon Review Insights is a full-stack NLP application that turns product reviews into useful customer feedback signals. The app provides sentiment analysis for single or multiple reviews, generates concise summaries from review batches, and presents the results in a clean responsive dashboard.

The project was built as an end-to-end data product: exploratory notebooks and model experiments live in the repository, while the production app is split into a FastAPI backend and a static frontend that can be deployed through Vercel.

## Live Links

- Frontend app: https://project3-amazon-review-insights-gpq863ecq-spqdots-projects.vercel.app/
- Backend API docs: https://project3-amazon-review-insights-1.onrender.com/docs#/analysis/analyze_single_analyze_post

## Features

- Analyze one review at a time for sentiment label and confidence score.
- Analyze review batches of up to 32 reviews.
- Summarize up to 100 reviews into a concise customer-feedback overview.
- Use OpenAI-powered sentiment analysis and summarization from the backend.
- Fall back to deterministic extractive summarization if OpenAI summarization is unavailable.
- Check backend health from the frontend.
- Configure the deployed backend URL directly from the frontend `API` button.
- Deploy the frontend as a static Vercel app.

## Example Review

```text
I like the design and performance, although the software is a bit buggy and setup was confusing.
```

## Tech Stack

Frontend:

- HTML
- CSS
- JavaScript
- Vercel static hosting

Backend:

- Python
- FastAPI
- Pydantic
- Uvicorn
- OpenAI API

Project workflow:

- Jupyter notebooks for data exploration and experiments
- GitHub for version control
- Vercel for frontend CI/CD
- Backend deployable to services such as Render, Railway, Hugging Face Spaces, Fly.io, or Google Cloud Run

## Project Structure

```text
Project3_amazon-review-insights/
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- config.py
|   |   |-- schemas.py
|   |   `-- services/
|   |       |-- analyzer.py
|   |       `-- summarizer.py
|   |-- requirements.txt
|   |-- Dockerfile
|   `-- .env.example
|-- frontend/
|   |-- index.html
|   |-- style.css
|   |-- script.js
|   `-- vercel.json
|-- notebooks/
|-- data/
|-- models/
|-- outputs/
`-- README.md
```

## Backend API

Base URL:

```text
http://localhost:8000
```

### Health Check

```http
GET /health
```

Returns the backend status, app metadata, configured model name, and whether the AI service is available.

### Analyze One Review

```http
POST /analyze
Content-Type: application/json
```

Request:

```json
{
  "text": "The product arrived quickly and works perfectly."
}
```

Response:

```json
{
  "result": {
    "label": "POSITIVE",
    "score": 0.98,
    "text_snippet": "The product arrived quickly and works perfectly."
  }
}
```

### Analyze Review Batch

```http
POST /analyze/batch
Content-Type: application/json
```

Request:

```json
{
  "texts": [
    "Great battery life and easy setup.",
    "I like the design and performance, although the software is a bit buggy and setup was confusing.",
    "The package arrived yesterday. I haven't used the product enough to form an opinion yet.",
    "Packaging was damaged and customer support was slow."
  ]
}
```

Response:

```json
{
  "results": [
    {
      "label": "POSITIVE",
      "score": 0.97,
      "text_snippet": "Great battery life and easy setup."
    },
    {
      "label": "NEUTRAL",
      "score": 0.86,
      "text_snippet": "I like the design and performance, although the software is a bit buggy and setup was confusing."
    },
    {
      "label": "NEUTRAL",
      "score": 0.82,
      "text_snippet": "The package arrived yesterday. I haven't used the product enough to form an opinion yet."
    },
    {
      "label": "NEGATIVE",
      "score": 0.94,
      "text_snippet": "Packaging was damaged and customer support was slow."
    }
  ],
  "total": 4
}
```

### Summarize Reviews

```http
POST /summarize
Content-Type: application/json
```

Request:

```json
{
  "texts": [
    "Customers like the battery life.",
    "Several buyers mention weak packaging.",
    "A few users had issues with customer support."
  ],
  "max_sentences": 3
}
```

Response:

```json
{
  "summary": "Customers generally like the battery life, but packaging and support are common pain points.",
  "method": "openai"
}
```

## Local Setup

### 1. Clone The Repository

```bash
git clone https://github.com/spqdot/Project3_amazon-review-insights.git
cd Project3_amazon-review-insights
```

### 2. Configure The Backend

```bash
cd backend
copy .env.example .env
```

On macOS/Linux, use:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI key:

```text
OPENAI_API_KEY=your_openai_api_key_here
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### 3. Install Backend Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run The Backend

From the `backend/` folder:

```bash
uvicorn app.main:app --reload
```

The API should run at:

```text
http://localhost:8000
```

Open the automatic API documentation at:

```text
http://localhost:8000/docs
```

### 5. Run The Frontend Locally

Open `frontend/index.html` in the browser, or serve the folder with a small static server.

From the project root:

```bash
python -m http.server 5500 -d frontend
```

Then open:

```text
http://localhost:5500
```

Use the `API` button in the top-right corner and set:

```text
http://localhost:8000
```

## Deployment

### Frontend On Vercel

The frontend is a static app in `frontend/`, so Vercel can deploy it directly from GitHub.

Recommended Vercel settings:

- Framework preset: `Other`
- Root directory: `frontend`
- Build command: leave empty
- Output directory: leave empty or use `.`

After deployment, open the Vercel app and click the `API` button. Set it to your deployed backend URL, for example:

```text
https://your-backend-service.com
```

Vercel CI/CD:

- Every push to `main` triggers a new production deployment.
- Pull requests can create preview deployments.
- The frontend can remain fully static.

### Backend Deployment

The backend can be deployed to any Python-friendly platform that supports FastAPI.

Good options:

- Railway
- Hugging Face Spaces
- Fly.io
- Google Cloud Run
- Render

Required backend environment variables:

```text
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=256
CORS_ORIGINS=https://your-vercel-app.vercel.app
APP_NAME=Amazon Review Insights API
APP_VERSION=1.0.0
DEBUG=false
```

For local development, `CORS_ORIGINS=*` is acceptable. For production, use your exact Vercel URL.

## Notes About Large Files

The repository ignores generated model artifacts and serialized files such as:

- `.pkl`
- `.safetensors`
- `.bin`
- virtual environments
- local data/model folders

This keeps the GitHub repository lightweight and avoids GitHub's 100 MB file-size limit.

## Troubleshooting

### Frontend Shows `API offline`

Check that:

- The backend is running.
- The API URL in the frontend `API` settings is correct.
- The backend allows your frontend URL in `CORS_ORIGINS`.
- The backend `/health` endpoint works in the browser.

### Backend Returns OpenAI Errors

Check that:

- `OPENAI_API_KEY` is set.
- The key is valid.
- The selected `OPENAI_MODEL` is available for your account.
- Your account has enough API credits or billing enabled.

### Vercel Deploys But The App Cannot Analyze Reviews

Vercel only hosts the frontend. The backend must be deployed separately, and the frontend must be configured with the deployed backend URL.

## Author

Created by Shrabani as part of the IronHack Week 6 Project 3 work.
