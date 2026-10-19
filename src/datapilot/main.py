
from fastapi import FastAPI

from datapilot.config import get_settings

settings = get_settings()

# Create the API application using centralized settings.
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {
        "status": "ok",
        "service": settings.app_name,
    }


@app.get("/")
def root() -> dict[str, str]:
    """Return basic API information."""
    return {
        "app": settings.app_name,
        "message": "Welcome to DataPilot",
        "health": "/health",
        "docs": "/docs",
    }