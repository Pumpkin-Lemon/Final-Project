
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.api.routes import router


app = FastAPI(
    title="SciTutor Workbench API",
    version="3.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Existing API routes
app.include_router(router, prefix="/api/v3")


# Existing health check
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "scitutor-api",
    }


# Serve Frontend from the same origin as the API
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
