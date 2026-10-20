from fastapi import FastAPI

app = FastAPI(
    title="DataLens AI API",
    description="Automated CSV exploratory data analysis and insights.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "DataLens AI"}
