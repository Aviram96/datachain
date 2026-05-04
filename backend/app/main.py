from fastapi import FastAPI

app = FastAPI(
    title="Datachain API",
    description="Ingest and metadata API for Datachain (Epic 1 scaffold).",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe for local dev and orchestration."""
    return {"status": "ok"}
