from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from app.eda import profile_csv
from app.services.data_quality import analyze_data_quality
from app.services.insights import (
    build_insights_evidence,
    generate_dataset_insights,
)
from app.services.llm_client import LLMConfigurationError, LLMProviderError
from app.services.report import generate_html_report, generate_pdf_report
from app.services.visualization import (
    create_box_plot,
    create_correlation_heatmap,
    create_histogram,
    detect_outliers,
)

load_dotenv()

app = FastAPI(
    title="DataLens AI API",
    description="Automated CSV exploratory data analysis and insights.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "DataLens AI"}


async def read_csv_request(request: Request) -> str:
    """Decode an uploaded CSV request body as UTF-8."""
    try:
        return (await request.body()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="CSV must use UTF-8 encoding.",
        ) from exc


def png_response(image_bytes: bytes) -> Response:
    return Response(content=image_bytes, media_type="image/png")


@app.post(
    "/api/v1/eda/profile",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"text/csv": {"schema": {"type": "string"}}},
        }
    },
)
async def create_eda_profile(request: Request):
    csv_content = await read_csv_request(request)
    try:
        return profile_csv(csv_content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/eda/visualizations/histogram")
async def histogram(request: Request, column: str):
    csv_content = await read_csv_request(request)
    try:
        return png_response(create_histogram(csv_content, column))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/eda/visualizations/box-plot")
async def box_plot(request: Request, column: str):
    csv_content = await read_csv_request(request)
    try:
        return png_response(create_box_plot(csv_content, column))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/eda/visualizations/correlation-heatmap")
async def correlation_heatmap(request: Request):
    csv_content = await read_csv_request(request)
    try:
        return png_response(create_correlation_heatmap(csv_content))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/eda/outliers")
async def outliers(request: Request, column: str):
    csv_content = await read_csv_request(request)
    try:
        return detect_outliers(csv_content, column)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/api/v1/eda/report/html",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"text/csv": {"schema": {"type": "string"}}},
        }
    },
)
async def html_report(request: Request):
    """Generate a downloadable, self-contained HTML EDA report."""
    csv_content = await read_csv_request(request)
    try:
        report = generate_html_report(csv_content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=report,
        media_type="text/html",
        headers={
            "Content-Disposition": 'attachment; filename="datalens-eda-report.html"'
        },
    )


@app.post(
    "/api/v1/eda/data-quality",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"text/csv": {"schema": {"type": "string"}}},
        }
    },
)
async def data_quality(request: Request):
    """Analyze data-quality issues in an uploaded CSV."""
    csv_content = await read_csv_request(request)
    try:
        return analyze_data_quality(csv_content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post(
    "/api/v1/eda/report/pdf",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"text/csv": {"schema": {"type": "string"}}},
        }
    },
)
async def pdf_report(request: Request):
    """Generate a downloadable PDF EDA report."""
    csv_content = await read_csv_request(request)
    try:
        report = generate_pdf_report(csv_content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return Response(
        content=report,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="datalens-eda-report.pdf"'
        },
    )


@app.post(
    "/api/v1/eda/insights/evidence",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"text/csv": {"schema": {"type": "string"}}},
        }
    },
)
async def insights_evidence(request: Request):
    """Build an evidence package for grounded dataset insights."""
    csv_content = await read_csv_request(request)
    try:
        return build_insights_evidence(csv_content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
@app.post(
    "/api/v1/eda/insights",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"text/csv": {"schema": {"type": "string"}}},
        }
    },
)
async def ai_insights(request: Request):
    """Generate AI-powered insights grounded in deterministic EDA evidence."""
    csv_content = await read_csv_request(request)

    try:
        return await generate_dataset_insights(csv_content)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

