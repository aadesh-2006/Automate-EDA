
# Automate-EDA

Automated exploratory data analysis for CSV datasets, with statistical profiling, visualizations, and outlier detection. AI-assisted, evidence-grounded insights are planned for a later stage.

## Current Features

- **CSV profiling:** row and column counts, column names, data types, unique values, and numeric statistical summaries.
- **Data quality:** missing-value counts and percentages, duplicate rows, constant columns, high-cardinality columns, and potential mixed numeric/text columns.
- **Visualizations:** PNG histograms, box plots, and correlation heatmaps.
- **HTML reports:** Downloadable, self-contained reports with dataset statistics and embedded charts.
- **Outlier detection:** identifies potential numeric outliers using the 1.5×IQR rule.
- **Input validation:** rejects empty CSV content, invalid UTF-8, missing columns, and unsupported numeric data.
- **REST API:** FastAPI endpoints with automated tests.

## Tech Stack

- **Backend:** Python 3.13+, FastAPI, Pandas, NumPy, SciPy
- **Visualizations:** Matplotlib
- **Testing:** Pytest, FastAPI TestClient, HTTPX
- **Planned frontend:** React, TypeScript, Vite
- **Planned AI:** Compatible open-weight model for evidence-grounded explanations

## Getting Started

### Prerequisites

- Python 3.13 or a compatible supported Python version
- Git

### Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/aadesh-2006/Automate-EDA.git
cd Automate-EDA
```

Create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the backend dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

### Run the API

From the repository root, set the backend directory on Python's module path and start the development server.

**Windows PowerShell**

```powershell
$env:PYTHONPATH = "backend"
python -m uvicorn app.main:app --reload --app-dir backend
```

**macOS / Linux**

```bash
PYTHONPATH=backend python -m uvicorn app.main:app --reload --app-dir backend
```

The API runs at `http://127.0.0.1:8000`.

- Health check: `GET /health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

## API Reference

CSV endpoints accept raw CSV text in the request body. Send `Content-Type: text/csv`. Image endpoints return PNG bytes; the outlier endpoint returns JSON.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/api/v1/eda/profile` | Return dataset profile and statistical summaries |
| POST | `/api/v1/eda/visualizations/histogram?column=age` | Generate a histogram for a numeric column |
| POST | `/api/v1/eda/visualizations/box-plot?column=age` | Generate a box plot for a numeric column |
| POST | `/api/v1/eda/visualizations/correlation-heatmap` | Generate a heatmap for numeric columns |
| POST | `/api/v1/eda/outliers?column=age` | Detect outliers in a numeric column |
| POST | `/api/v1/eda/data-quality` | Identify data-quality issues and suspicious columns |
| POST | `/api/v1/eda/report/html` | Download a standalone HTML EDA report |

### Examples

Check the API health:

```bash
curl http://127.0.0.1:8000/health
```

Get a profile from a CSV file:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/profile" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

Generate a histogram and save the returned PNG:

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

Analyze data quality:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/data-quality" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

Detect outliers:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/outliers?column=age" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv"
```

Download a standalone HTML report:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/eda/report/html" \
  -H "Content-Type: text/csv" \
  --data-binary "@sample.csv" \
  --output datalens-eda-report.html
```

Replace `sample.csv` with your CSV file. The requested column must exist and contain numeric values for histogram, box plot, and outlier detection. The correlation heatmap requires at least two columns containing numeric values.

Invalid input returns HTTP `400` with a JSON `detail` message.

## Run Tests

From the repository root:

```bash
python -m pytest backend/tests -v
```

## Roadmap

- [x] Backend health endpoint and tests
- [x] Deterministic EDA engine
- [x] CSV profiling API and input validation
- [x] Histograms and box plots
- [x] Correlation heatmaps
- [x] IQR-based outlier detection
- [x] API integration tests
- [x] More comprehensive data-quality checks
- [x] Downloadable HTML report
- [ ] Downloadable PDF reports
- [ ] Evidence-grounded insights using a compatible open-weight model
- [ ] React dashboard and end-to-end testing

## Contributing

Issues and pull requests are welcome. Please run the test suite before submitting changes.
