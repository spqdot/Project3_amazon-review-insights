# Amazon Review Insights

NLP project for sentiment analysis and summarization of Amazon product reviews.

## Frontend deployment on Vercel

The frontend is a static app in `frontend/`.

Vercel settings:

- Framework preset: `Other`
- Root directory: `frontend`
- Build command: leave empty
- Output directory: leave empty or use `.`

After deployment, open the app and use the `API` button in the top-right corner to set your deployed backend URL.

Backend CORS note: add your Vercel URL to the backend `CORS_ORIGINS` environment variable, for example:

```text
https://your-project.vercel.app
```
