
from fastapi import FastAPI, HTTPException, Request

from app.eda import profile_csv

app = FastAPI(
    title="DataLens AI API",
    description="Automated CSV exploratory data analysis and insights.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "DataLens AI"}


@app.post(
    "/api/v1/eda/profile",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "text/csv": {
                    "schema": {"type": "string"},
                }
            },
        }
    },
)
async def create_eda_profile(request: Request):
    try:
        csv_content = (await request.body()).decode("utf-8-sig")
        return profile_csv(csv_content)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="CSV must use UTF-8 encoding.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
