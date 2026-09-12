from app.routes.candidates import router as candidates_router
from app.routes.jobs import router as jobs_router
from app.routes.ranking import router as ranking_router

__all__ = ["candidates_router", "jobs_router", "ranking_router"]