"""Reminders router - manage notification channels."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models import Reminder, LearningPlan

router = APIRouter()


class ReminderConfigResponse(BaseModel):
    channel: str
    config: dict = {}


class ReminderConfigUpdate(BaseModel):
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    channel_id: Optional[str] = None


@router.get("/config/{channel}", response_model=ReminderConfigResponse)
def get_reminder_config(channel: str, db: Session = Depends(get_db)):
    """获取提醒渠道配置。"""
    reminder = db.query(Reminder).filter(
        Reminder.channel == channel
    ).first()
    
    if reminder:
        return ReminderConfigResponse(
            channel=channel,
            config=reminder.channel_config or {}
        )
    return ReminderConfigResponse(channel=channel, config={})


@router.put("/config/{channel}")
def save_reminder_config(channel: str, config: ReminderConfigUpdate, db: Session = Depends(get_db)):
    """保存提醒渠道配置。"""
    reminder = db.query(Reminder).filter(
        Reminder.channel == channel
    ).first()
    
    config_dict = config.model_dump(exclude_none=True)
    
    if reminder:
        reminder.channel_config = config_dict
    else:
        reminder = Reminder(
            plan_id=1,  # 默认计划
            channel=channel,
            channel_config=config_dict,
            enabled=True
        )
        db.add(reminder)
    
    db.commit()
    return {"ok": True, "channel": channel}


@router.get("/plan/{plan_id}")
def list_reminders(plan_id: int, db: Session = Depends(get_db)):
    return db.query(Reminder).filter(Reminder.plan_id == plan_id).all()


@router.post("/plan/{plan_id}")
def add_reminder(plan_id: int, data: dict, db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")

    db_reminder = Reminder(
        plan_id=plan_id,
        channel=data.get("channel", "dingtalk"),
        channel_config=data.get("channel_config", {}),
        enabled=data.get("enabled", True),
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


@router.put("/{reminder_id}/toggle")
def toggle_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    reminder.enabled = not reminder.enabled
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"ok": True}


@router.post("/test/{channel}")
def test_reminder(channel: str, db: Session = Depends(get_db)):
    """Send a test notification to verify channel works."""
    from ..services.notifiers import send_notification

    success, msg = send_notification(
        channel=channel,
        title="LearnFlow Test",
        body="If you see this, the notification channel is working!",
    )
    return {"success": success, "message": msg}
