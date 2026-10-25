# DataLens AI — AI-Powered Exploratory Data Analysis

**DataLens AI** is a full-stack data analysis platform that automates exploratory data analysis (EDA), identifies data-quality issues, generates visualizations and reports, and uses a **fine-tuned Qwen3:4B language model** to produce AI-assisted, evidence-grounded insights from tabular datasets.

The platform combines deterministic statistical analysis with a specialized language model to help users understand their datasets, discover patterns, investigate anomalies, and make data-informed decisions.

## Key Features

### 1. Automated Dataset Profiling
- Analyze CSV datasets through a web-based dashboard.
- Calculate row and column counts, data types, unique values, and numeric statistical summaries.
- Identify missing values and their percentages.
- Inspect dataset structure before performing deeper analysis.

### 2. Data Quality Analysis
- Detect missing values and duplicate rows.
- Identify constant columns and high-cardinality features.
- Flag potential mixed-type columns.
- Generate structured data-quality findings to support data cleaning and preprocessing.

### 3. Interactive Data Visualizations
- **Histograms:** Explore numeric feature distributions.
- **Box plots:** Inspect spread, quartiles, and potential outliers.
- **Correlation heatmaps:** Investigate relationships between numeric features.
- Use visual evidence to investigate unusual patterns and relationships in the data.

### 4. Outlier Detection
- Detect potential numeric outliers using the 1.5×IQR rule.
- Identify observations outside the calculated interquartile bounds.
- Support further investigation of anomalous values.

### 5. Downloadable EDA Reports
- Generate standalone HTML reports.
- Export PDF reports containing dataset statistics and visualizations.
- Share analysis results outside the dashboard.

### 6. Fine-Tuned AI Data Analyst

DataLens AI integrates a **fine-tuned Qwen3:4B model** for specialized data-analysis assistance.

The AI layer is designed to interpret structured statistical evidence and communicate findings in a useful, understandable format.

Key objectives include:
- Interpreting distributions, skewness, and statistical summaries.
- Explaining potential outliers and data-quality problems.
- Interpreting feature correlations without automatically treating them as causal relationships.
- Summarizing evidence-backed patterns and suggesting follow-up analyses.
- Producing structured analytical responses for integration with the application.

The system combines deterministic Python-based analysis with language-model reasoning. Statistical calculations are handled by the analysis pipeline, while the language model helps interpret and explain the results.

**Model:** Qwen3:4B, fine-tuned for the DataLens AI project.

**Local inference:** Ollama with an OpenAI-compatible API interface.

> Fine-tuning methodology, training dataset composition, adapter details, and quantitative benchmark results should be documented alongside the actual training artifacts and evaluation results.

### 7. REST API
- FastAPI-based backend.
- Structured endpoints for profiling, data quality, visualizations, outlier detection, reports, and AI insights.
- Automated backend tests.

### 8. Full-Stack Dashboard
- React and TypeScript frontend.
- Vite development environment.
- Tailwind CSS for styling.
- Recharts for chart-based data exploration.
- Axios for API communication.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS |
| Charts | Recharts |
| HTTP client | Axios |
| Backend | Python, FastAPI |
| Data analysis | Pandas, NumPy, SciPy |
| Visualization and reports | Matplotlib, HTML, PDF |
| Language model | Fine-tuned Qwen3:4B |
| Local inference | Ollama |
| Training environment | Kaggle GPU notebook, if used for the completed training run |
| Testing | Pytest, FastAPI TestClient, HTTPX |
| Version control | Git, GitHub |

## System Architecture

```text
                     CSV Dataset
                          |
                          v
               React + TypeScript UI
                          |
                          v
                    FastAPI Backend
                          |
            +-------------+-------------+
            |             |             |
            v             v             v
       Data Profiling  Data Quality  Visualizations
            |             |             |
            +-------------+-------------+
                          |
            +-------------+-------------+
            |             |             |
            v             v             v
       Outlier         HTML/PDF      Evidence
       Detection       Reports       Generation
                                         |
                                         v
                               Fine-Tuned Qwen3:4B
                                         |
                                         v
                                  AI Insights
                                         |
                                         v
                                 Dashboard Output
```

## Getting Started

### Prerequisites

- Python version supported by the backend dependencies.
- Node.js and npm.
- Git.
- Ollama and the configured fine-tuned model for local AI inference.

### 1. Clone the Repository

```bash
git clone https://github.com/aadesh-2006/Automate-EDA.git
cd Automate-EDA
```

### 2. Install Backend Dependencies

Create a virtual environment from the repository root.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

### 3. Configure the Language Model

Install Ollama and ensure the fine-tuned Qwen3:4B model is available locally.

If the fine-tuned model has been packaged under a custom Ollama model name, use that name in the configuration. Do not assume that the original `qwen3:4b` tag automatically refers to the fine-tuned version.

Create a `.env` file in the repository root:

```dotenv
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen3:4b
```

Set `LLM_MODEL` to the actual Ollama tag that points to the fine-tuned model, if it differs from `qwen3:4b`.

Keep `.env` local and do not commit private configuration or credentials.

### 4. Start the Backend

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

- Health endpoint: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 5. Start the Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

The frontend development server proxies supported API requests to the local backend.

## API Reference

CSV analysis endpoints accept raw CSV text in the request body with `Content-Type: text/csv`, unless otherwise noted.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend health |
| POST | `/api/v1/eda/profile` | Dataset profile and numeric summaries |
| POST | `/api/v1/eda/data-quality` | Data-quality analysis |
| POST | `/api/v1/eda/visualizations/histogram?column=age` | Generate a histogram |
| POST | `/api/v1/eda/visualizations/box-plot?column=age` | Generate a box plot |
| POST | `/api/v1/eda/visualizations/correlation-heatmap` | Generate a numeric correlation heatmap |
| POST | `/api/v1/eda/outliers?column=age` | Detect potential outliers |
| POST | `/api/v1/eda/report/html` | Generate an HTML report |
| POST | `/api/v1/eda/report/pdf` | Generate a PDF report |
| POST | `/api/v1/eda/insights/evidence` | Generate structured deterministic evidence |
| POST | `/api/v1/eda/insights` | Generate AI-assisted insights |

For endpoints that accept a column query parameter, replace `age` with an appropriate column name in your CSV.

### Example: Profile a Dataset

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/profile" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

### Example: Analyze Data Quality

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/data-quality" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

### Example: Generate a Histogram

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/visualizations/histogram?column=age" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output histogram.png
```

### Example: Generate a Correlation Heatmap

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/visualizations/correlation-heatmap" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output correlation-heatmap.png
```

### Example: Export a Report

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/report/html" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output datalens-report.html
```

For PDF output, use `/api/v1/eda/report/pdf` and save the response as a `.pdf` file.

Replace `sample.csv` with your dataset path. Numeric visualization and outlier endpoints require an appropriate numeric column.

## Datasets and Validation

DataLens AI is intended to support diverse tabular datasets, including sensor telemetry, retail transactions, marketing data, and other structured datasets.

Candidate datasets for testing and benchmarking include:

- Smart-home sensor and occupancy datasets.
- Wine Quality.
- Adult Census Income.
- Bank Marketing.
- Student Performance.
- Bike Sharing.
- NASA C-MAPSS turbofan sensor data.
- IEEE-CIS Fraud Detection.
- Instacart Market Basket Analysis.
- Airbnb listing data.
- NYC Yellow Taxi trip records.

Dataset use should be recorded accurately: a dataset used to validate EDA functionality is not automatically a model-training dataset. Large datasets may require sampling, preprocessing, or memory-efficient ingestion.

## Testing

### Backend

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```

### Frontend

Run from the `frontend` directory:

```powershell
npm run lint
npm run build
```

### AI Model Evaluation

The fine-tuned model should be evaluated against the original base model using the same held-out examples. Useful evaluation dimensions include:

- Statistical interpretation correctness.
- Agreement with computed evidence.
- Unsupported-claim and hallucination rate.
- Structured-output validity.
- Usefulness and relevance of recommendations.
- Inference latency and resource usage.

Publish quantitative results only after running the evaluation and recording the actual measurements.

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

This is a high-level overview; additional modules and model artifacts may exist in the actual repository.

## Engineering Principles

- **Evidence before explanation:** calculate statistics using deterministic code before asking the language model to interpret them.
- **Reproducibility:** document model versions, training configuration, datasets, random seeds, and evaluation splits.
- **No unsupported causal claims:** correlation and feature importance do not independently prove causation.
- **Privacy-aware processing:** handle sensitive datasets carefully and avoid exposing confidential data through external services.
- **Honest evaluation:** distinguish implemented functionality, tested behavior, and measured model improvements.

## Future Improvements

- Advanced multi-feature visualizations and comparisons.
- Predictive feature importance and model-assisted what-if analysis.
- Expanded evaluation benchmarks for fine-tuned AI insights.
- Improved large-dataset ingestion and memory efficiency.
- Reproducible model packaging and deployment.

## Contributing

Issues and pull requests are welcome. Run relevant backend tests and frontend checks before submitting changes.

## License

Refer to the repository's `LICENSE` file for usage and redistribution terms. If no license is present, the project has not yet specified an open-source license.
