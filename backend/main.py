import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from utils.config import config
from utils.logger import log
from backend.database.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.init_dirs()
    init_db()
    log.info("Medical Report AI Backend started")
    yield
    log.info("Medical Report AI Backend shutting down")


app = FastAPI(
    title="Medical Report AI - API",
    description="Enterprise-grade Medical Report Generation from Chest X-ray Images",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


from backend.api.auth_routes import router as auth_router
from backend.api.prediction_routes import router as prediction_router
from backend.api.analytics_routes import router as analytics_router
from backend.api.report_routes import router as report_router

app.include_router(auth_router)
app.include_router(prediction_router)
app.include_router(analytics_router)
app.include_router(report_router)


@app.get("/")
def root():
    return {
        "service": "Medical Report AI",
        "version": "2.0.0",
        "status": "operational",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
