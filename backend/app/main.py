import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes.candidates import router as candidates_router
from app.routes.jobs import router as jobs_router
from app.routes.ranking import router as ranking_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    init_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AI Resume Screening and Candidate Ranking System",
    description="AI-powered resume screening and candidate ranking API for HR recruiters.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
os.makedirs(frontend_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=frontend_dir, html=True), name="static")

# Include routers
app.include_router(candidates_router)
app.include_router(jobs_router)
app.include_router(ranking_router)


@app.get("/")
def root():
    return {
        "message": "AI Resume Screening and Candidate Ranking System",
        "docs": "/docs",
        "dashboard": "/static/index.html",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/weights")
def get_weights():
    return {"scoring_weights": settings.SCORING_WEIGHTS}