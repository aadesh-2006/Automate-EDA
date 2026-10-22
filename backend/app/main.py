
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response

from app.eda import profile_csv
from app.services.visualization import (
    create_box_plot,
    create_correlation_heatmap,
    create_histogram,
    detect_outliers,
)

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
