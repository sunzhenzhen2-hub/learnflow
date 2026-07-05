"""Achievements router - 成就系统（Keep 式）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Achievement
from ..schemas import AchievementResponse

router = APIRouter()


@router.get("/plan/{plan_id}", response_model=list[AchievementResponse])
def list_achievements(plan_id: int, db: Session = Depends(get_db)):
    """获取某计划的所有成就。"""
    return db.query(Achievement).filter(
        Achievement.plan_id == plan_id
    ).order_by(Achievement.unlocked_at.desc()).all()
