"""Reminders router - manage notification channels."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Reminder, LearningPlan
from ..schemas import ReminderCreate, ReminderResponse

router = APIRouter()


@router.get("/plan/{plan_id}", response_model=list[ReminderResponse])
def list_reminders(plan_id: int, db: Session = Depends(get_db)):
    return db.query(Reminder).filter(Reminder.plan_id == plan_id).all()


@router.post("/plan/{plan_id}", response_model=ReminderResponse)
def add_reminder(plan_id: int, reminder: ReminderCreate, db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")

    db_reminder = Reminder(
        plan_id=plan_id,
        channel=reminder.channel,
        channel_config=reminder.channel_config,
        enabled=reminder.enabled,
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


@router.put("/{reminder_id}/toggle", response_model=ReminderResponse)
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
