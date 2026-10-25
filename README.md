# DataLens AI — Automated Exploratory Data Analysis

**DataLens AI** is a full-stack exploratory data analysis platform that helps users profile CSV datasets, identify data-quality issues, visualize distributions and relationships, detect outliers, generate reports, and obtain AI-assisted insights grounded in dataset evidence.

The project combines a React dashboard, a FastAPI backend, deterministic statistical analysis, and an OpenAI-compatible LLM interface for AI-generated insights.

## Features

### Dataset Profiling
- Upload and analyze CSV datasets.
- View row counts, column counts, column names, data types, unique values, and numeric summaries.
- Inspect missing-value counts and percentages.

### Data Quality Analysis
- Detect missing values and duplicate rows.
- Identify constant columns and high-cardinality columns.
- Flag potential mixed-type columns.
- Review structured data-quality findings.

### Visualizations
- Generate histograms for numeric columns.
- Generate box plots to inspect distributions and potential outliers.
- Explore correlations between numeric features with correlation heatmaps.
- Render visualizations through the dashboard and backend API.

### Outlier Detection
- Detect potential numeric outliers using the 1.5×IQR rule.
- Inspect statistical evidence for unusual observations.

### Reports
- Generate downloadable standalone HTML EDA reports.
- Generate downloadable PDF reports containing dataset analysis and visualizations.

### AI-Assisted Insights
- Build structured, deterministic evidence from dataset profiles and data-quality checks.
- Generate AI-assisted explanations through an OpenAI-compatible chat-completions API.
- Configure a local LLM using Ollama, including Qwen3:4B.
- Keep statistical evidence separate from AI-generated interpretations.

**Interpretation note:** Correlation does not establish causation. Statistical findings and model-generated explanations should be interpreted in the context of the dataset.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| UI and charts | Tailwind CSS, Recharts, Lucide React |
| API requests | Axios |
| Backend | Python, FastAPI |
| Data analysis | Pandas, NumPy, SciPy |
| Visualization and reports | Matplotlib, HTML, PDF |
| AI integration | OpenAI-compatible API, Ollama, Qwen3:4B |
| Testing | Pytest, FastAPI TestClient, HTTPX |
| Version control | Git, GitHub |

## Architecture

```text
CSV Dataset
    |
    v
React + TypeScript Dashboard
    |
    v
FastAPI REST API
    |
    +---- Dataset Profiling
    |
    +---- Data Quality Analysis
    |
    +---- Visualization Generation
    |
    +---- Outlier Detection
    |
    +---- HTML / PDF Reports
    |
    +---- Evidence Generation
               |
               v
       OpenAI-Compatible LLM
               |
               v
        AI-Assisted Insights
```

## Getting Started

### Prerequisites

- Python with a version supported by the backend dependencies.
- Node.js and npm.
- Git.
- Ollama and a compatible model if you want to use local AI insights.

### 1. Clone the Repository

```bash
git clone https://github.com/aadesh-2006/Automate-EDA.git
cd Automate-EDA
```

### 2. Set Up the Backend

Create a virtual environment from the repository root.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

Start the backend from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 3. Set Up the Frontend

Open a second terminal at the repository root.

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

The frontend development server proxies API requests to the backend at `http://127.0.0.1:8000`.

### 4. Configure Local AI with Ollama

Install Ollama from [ollama.com](https://ollama.com/) and download the model:

```powershell
ollama pull qwen3:4b
```

Make sure Ollama is running and the model is available. Create a `.env` file in the **repository root**, alongside the backend and frontend directories:

```dotenv
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen3:4b
```

These variables configure the OpenAI-compatible endpoint, API key placeholder, and model name. Ollama normally runs locally at port `11434`.

Keep `.env` local. Do not commit credentials, private configuration, or other secrets to Git. The backend must load these variables before the AI client is initialized.

If AI insights fail to generate, check that Ollama is running, the model is downloaded, the environment variables are correct, and the backend has been restarted after configuration changes.

## API Reference

CSV analysis endpoints accept raw CSV text in the request body with `Content-Type: text/csv`, unless otherwise noted.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/api/v1/eda/profile` | Return dataset profiling and numeric summaries |
| POST | `/api/v1/eda/data-quality` | Analyze data-quality issues |
| POST | `/api/v1/eda/visualizations/histogram?column=age` | Generate a histogram |
| POST | `/api/v1/eda/visualizations/box-plot?column=age` | Generate a box plot |
| POST | `/api/v1/eda/visualizations/correlation-heatmap` | Generate a numeric correlation heatmap |
| POST | `/api/v1/eda/outliers?column=age` | Detect potential outliers |
| POST | `/api/v1/eda/report/html` | Generate a downloadable HTML report |
| POST | `/api/v1/eda/report/pdf` | Generate a downloadable PDF report |
| POST | `/api/v1/eda/insights/evidence` | Return structured, deterministic analysis evidence |
| POST | `/api/v1/eda/insights` | Generate AI-assisted insights from dataset evidence |

### API Examples

Check the API health:

```bash
curl http://127.0.0.1:8000/health
```

Profile a CSV dataset:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/profile" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

Analyze data quality:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/data-quality" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

Generate a histogram and save the PNG response:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/visualizations/histogram?column=age" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output histogram.png
```

Generate a correlation heatmap:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/visualizations/correlation-heatmap" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output correlation-heatmap.png
```

Download an HTML report:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/report/html" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output datalens-report.html
```

Download a PDF report:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/report/pdf" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output datalens-report.pdf
```

Replace `sample.csv` and `age` with your dataset filename and a numeric column present in the CSV.

## Development and Testing

### Backend Tests

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```

### Frontend Checks

Run from the `frontend` directory:

```powershell
npm run lint
npm run build
```

The production build runs TypeScript checks and creates the frontend bundle.

## Project Structure

```text
Automate-EDA/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── .env                  # Local configuration; do not commit
├── .gitignore
└── README.md
```

The tree above highlights the main application areas; individual modules and files may vary as development continues.

## Roadmap

- [x] FastAPI backend and health endpoint
- [x] CSV profiling and numeric summaries
- [x] Data-quality analysis
- [x] Histograms, box plots, and correlation heatmaps
- [x] IQR-based outlier detection
- [x] Downloadable HTML and PDF reports
- [x] React + TypeScript dashboard
- [x] Deterministic evidence-generation endpoint
- [x] OpenAI-compatible LLM configuration
- [ ] Validate the complete local Ollama-to-dashboard insights flow
- [ ] Multi-feature visualizations and improved feature comparisons
- [ ] Feature-importance analysis and evidence-backed what-if exploration
- [ ] Broader end-to-end testing and deployment

## Contributing

Issues and pull requests are welcome. Run the relevant backend tests and frontend checks before submitting changes.

## License

No license has been specified yet. Check the repository for a `LICENSE` file before reusing or redistributing this project.
