"""LearnFlow - AI-Driven Learning Execution System."""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session

from .database import init_db, get_db
from .routers import plans, steps, review, reminders, config, achievements, profile, auth
from .models import User
from .dependencies import get_current_user_or_none

app = FastAPI(title="LearnFlow", version="0.1.0")

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth router (login/logout/sessions)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Public routers (user context attached via optional auth)
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
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """Get dashboard data for the current user's active plan."""
    from .services.dashboard import get_dashboard_data
    user = current_user
    if not user:
        # Get or create guest user
        guest = db.query(User).filter(User.username == "guest").first()
        if not guest:
            from .services.auth import get_password_hash
            guest = User(
                username="guest",
                hashed_password=get_password_hash("guest"),
                is_active=True,
                is_admin=False,
            )
            db.add(guest)
            db.flush()
        user = guest
    return get_dashboard_data(user.id)


# Serve frontend static files in production
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
