"""LearnFlow - AI-Driven Learning Execution System."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database import init_db
from .routers import plans, steps, review, reminders, config, achievements, profile

app = FastAPI(title="LearnFlow", version="0.1.0")

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(plans.router, prefix="/api/plans", tags=["plans"])
app.include_router(steps.router, prefix="/api/steps", tags=["steps"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(achievements.router, prefix="/api/achievements", tags=["achievements"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])


@app.on_event("startup")
def startup():
    init_db()
    from .services.scheduler import start_scheduler
    start_scheduler()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "LearnFlow"}


@app.get("/api/dashboard")
def dashboard():
    """Get dashboard data for the active plan."""
    from .services.dashboard import get_dashboard_data
    return get_dashboard_data()


# Serve frontend static files in production
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
