const defaultApiBase = "http://localhost:8000";
let apiBase = localStorage.getItem("ari-api-base") || defaultApiBase;
let lastResults = [];

const samples = {
  positive:
    "This air fryer is fantastic. It heats evenly, cleans quickly, and the controls are simple enough for daily use.",
  mixed:
    "The camera quality is sharp and the battery lasts all day, but the app setup was confusing and the packaging arrived damaged.",
  negative:
    "The headphones stopped charging after two weeks. Customer support was slow and the replacement process was frustrating.",
};

const els = {
  healthStatus: document.querySelector("#healthStatus"),
  healthText: document.querySelector("#healthText"),
  settingsButton: document.querySelector("#settingsButton"),
  settingsDialog: document.querySelector("#settingsDialog"),
  apiBaseUrl: document.querySelector("#apiBaseUrl"),
  saveSettings: document.querySelector("#saveSettings"),
  tabs: document.querySelectorAll(".tab-button"),
  panels: {
    single: document.querySelector("#singlePanel"),
    batch: document.querySelector("#batchPanel"),
    summary: document.querySelector("#summaryPanel"),
  },
  singleReview: document.querySelector("#singleReview"),
  batchReviews: document.querySelector("#batchReviews"),
  summaryReviews: document.querySelector("#summaryReviews"),
  singleCount: document.querySelector("#singleCount"),
  batchCount: document.querySelector("#batchCount"),
  summaryCount: document.querySelector("#summaryCount"),
  sentenceCount: document.querySelector("#sentenceCount"),
  sentenceOutput: document.querySelector("#sentenceOutput"),
  analyzeButton: document.querySelector("#analyzeButton"),
  batchButton: document.querySelector("#batchButton"),
  summaryButton: document.querySelector("#summaryButton"),
  clearButton: document.querySelector("#clearButton"),
  emptyState: document.querySelector("#emptyState"),
  resultStack: document.querySelector("#resultStack"),
  positiveMetric: document.querySelector("#positiveMetric"),
  negativeMetric: document.querySelector("#negativeMetric"),
  confidenceMetric: document.querySelector("#confidenceMetric"),
  toast: document.querySelector("#toast"),
};

function endpoint(path) {
  return `${apiBase.replace(/\/$/, "")}${path}`;
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => els.toast.classList.remove("visible"), 3200);
}

function setLoading(button, loading, text) {
  if (!button.dataset.label) {
    button.dataset.label = button.textContent;
  }
  button.disabled = loading;
  button.textContent = loading ? text : button.dataset.label;
}

function splitReviews(value) {
  return value
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

async function request(path, options = {}) {
  const response = await fetch(endpoint(path), {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the HTTP status message.
    }
    throw new Error(Array.isArray(message) ? message.map((item) => item.msg).join(" ") : message);
  }

  return response.json();
}

async function checkHealth() {
  els.healthStatus.classList.remove("online", "offline");
  els.healthText.textContent = "Checking API";

  try {
    const health = await request("/health");
    els.healthStatus.classList.add("online");
    els.healthText.textContent = health.model_loaded ? "AI ready" : "API online";
  } catch {
    els.healthStatus.classList.add("offline");
    els.healthText.textContent = "API offline";
  }
}

function setActiveTab(tabName) {
  els.tabs.forEach((button) => {
    const active = button.dataset.tab === tabName;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });

  Object.entries(els.panels).forEach(([name, panel]) => {
    const active = name === tabName;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });
}

function sentimentClass(label = "") {
  const normalized = label.toLowerCase();
  if (normalized.includes("pos") || normalized === "5 stars" || normalized === "4 stars") return "positive";
  if (normalized.includes("neg") || normalized === "1 star" || normalized === "2 stars") return "negative";
  return "neutral";
}

function resultCard(result, index) {
  const score = Math.round((result.score || 0) * 100);
  const labelClass = sentimentClass(result.label);
  const snippet = result.text_snippet || "No snippet returned.";

  return `
    <article class="result-card">
      <div class="result-title">
        <strong>Review ${index + 1}</strong>
        <span class="label-badge ${labelClass}">${result.label}</span>
      </div>
      <div class="confidence-bar" aria-label="Confidence ${score}%">
        <span style="width: ${score}%"></span>
      </div>
      <p class="snippet">${score}% confidence - ${escapeHtml(snippet)}</p>
    </article>
  `;
}

function summaryCard(summary, method) {
  return `
    <article class="result-card">
      <div class="result-title">
        <strong>Review summary</strong>
        <span class="label-badge neutral">${method}</span>
      </div>
      <p class="summary-text">${escapeHtml(summary)}</p>
    </article>
  `;
}

function batchCard(results) {
  const rows = results
    .map((result, index) => {
      const score = Math.round((result.score || 0) * 100);
      return `
        <tr>
          <td>${index + 1}</td>
          <td><span class="label-badge ${sentimentClass(result.label)}">${result.label}</span></td>
          <td>${score}%</td>
          <td>${escapeHtml(result.text_snippet || "")}</td>
        </tr>
      `;
    })
    .join("");

  return `
    <article class="result-card">
      <div class="result-title">
        <strong>Batch results</strong>
        <span class="label-badge neutral">${results.length} reviews</span>
      </div>
      <table class="batch-table">
        <thead>
          <tr><th>#</th><th>Sentiment</th><th>Score</th><th>Snippet</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </article>
  `;
}

function renderResults(html, metricResults = []) {
  els.emptyState.hidden = true;
  els.resultStack.hidden = false;
  els.resultStack.innerHTML = html;
  if (metricResults.length) {
    lastResults = metricResults;
    updateMetrics();
  }
}

function updateMetrics() {
  const positive = lastResults.filter((result) => sentimentClass(result.label) === "positive").length;
  const negative = lastResults.filter((result) => sentimentClass(result.label) === "negative").length;
  const avg = lastResults.length
    ? Math.round((lastResults.reduce((sum, result) => sum + Number(result.score || 0), 0) / lastResults.length) * 100)
    : null;

  els.positiveMetric.textContent = positive;
  els.negativeMetric.textContent = negative;
  els.confidenceMetric.textContent = avg === null ? "--" : `${avg}%`;
}

function clearResults() {
  lastResults = [];
  updateMetrics();
  els.resultStack.innerHTML = "";
  els.resultStack.hidden = true;
  els.emptyState.hidden = false;
}

function updateCounts() {
  els.singleCount.textContent = `${els.singleReview.value.length} / 5000`;
  els.batchCount.textContent = `${splitReviews(els.batchReviews.value).length} / 32`;
  els.summaryCount.textContent = `${splitReviews(els.summaryReviews.value).length} / 100`;
  els.sentenceOutput.value = els.sentenceCount.value;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function analyzeSingle() {
  const text = els.singleReview.value.trim();
  if (!text) {
    showToast("Add a review before analyzing.");
    return;
  }

  setLoading(els.analyzeButton, true, "Analyzing...");
  try {
    const data = await request("/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    renderResults(resultCard(data.result, 0), [data.result]);
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(els.analyzeButton, false);
  }
}

async function analyzeBatch() {
  const texts = splitReviews(els.batchReviews.value);
  if (!texts.length) {
    showToast("Add at least one review.");
    return;
  }
  if (texts.length > 32) {
    showToast("Batch analysis accepts up to 32 reviews.");
    return;
  }

  setLoading(els.batchButton, true, "Analyzing...");
  try {
    const data = await request("/analyze/batch", {
      method: "POST",
      body: JSON.stringify({ texts }),
    });
    renderResults(batchCard(data.results), data.results);
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(els.batchButton, false);
  }
}

async function summarizeReviews() {
  const texts = splitReviews(els.summaryReviews.value);
  if (!texts.length) {
    showToast("Add reviews to summarize.");
    return;
  }
  if (texts.length > 100) {
    showToast("Summary accepts up to 100 reviews.");
    return;
  }

  setLoading(els.summaryButton, true, "Summarizing...");
  try {
    const data = await request("/summarize", {
      method: "POST",
      body: JSON.stringify({
        texts,
        max_sentences: Number(els.sentenceCount.value),
      }),
    });
    renderResults(summaryCard(data.summary, data.method));
  } catch (error) {
    showToast(error.message);
  } finally {
    setLoading(els.summaryButton, false);
  }
}

els.tabs.forEach((button) => button.addEventListener("click", () => setActiveTab(button.dataset.tab)));
els.analyzeButton.addEventListener("click", analyzeSingle);
els.batchButton.addEventListener("click", analyzeBatch);
els.summaryButton.addEventListener("click", summarizeReviews);
els.clearButton.addEventListener("click", clearResults);

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => {
    els.singleReview.value = samples[button.dataset.sample];
    updateCounts();
    els.singleReview.focus();
  });
});

[els.singleReview, els.batchReviews, els.summaryReviews, els.sentenceCount].forEach((input) => {
  input.addEventListener("input", updateCounts);
});

els.settingsButton.addEventListener("click", () => {
  els.apiBaseUrl.value = apiBase;
  els.settingsDialog.showModal();
});

els.saveSettings.addEventListener("click", () => {
  const nextBase = els.apiBaseUrl.value.trim() || defaultApiBase;
  apiBase = nextBase;
  localStorage.setItem("ari-api-base", nextBase);
  showToast("API URL saved.");
  checkHealth();
});

updateCounts();
updateMetrics();
checkHealth();
