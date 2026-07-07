"""Achievements router - 成就系统（Keep 式）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Achievement, LearningPlan, User
from ..schemas import AchievementResponse
from ..dependencies import get_current_user_or_none

router = APIRouter()


def _get_or_create_guest_user(db: Session) -> User:
    """获取或创建访客用户（用于向后兼容未登录用户）。"""
    guest = db.query(User).filter(User.username == "guest").first()
    if not guest:
        from ..services.auth import get_password_hash
        guest = User(
            username="guest",
            hashed_password=get_password_hash("guest"),
            is_active=True,
            is_admin=False,
        )
        db.add(guest)
        db.flush()
    return guest


@router.get("/plan/{plan_id}", response_model=list[AchievementResponse])
def list_achievements(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """获取某计划的所有成就（需属于当前用户）。"""
    user = current_user or _get_or_create_guest_user(db)
    plan = db.query(LearningPlan).filter(
        LearningPlan.id == plan_id,
        LearningPlan.user_id == user.id,
    ).first()
    if not plan:
        raise HTTPException(404, "Plan not found")
    return db.query(Achievement).filter(
        Achievement.plan_id == plan_id
    ).order_by(Achievement.unlocked_at.desc()).all()
