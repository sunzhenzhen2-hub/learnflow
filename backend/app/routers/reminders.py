"""Reminders router - manage notification channels."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models import Reminder, LearningPlan, User
from ..dependencies import get_current_user_or_none

router = APIRouter()


class ReminderConfigResponse(BaseModel):
    channel: str
    config: dict = {}


class ReminderConfigUpdate(BaseModel):
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    channel_id: Optional[str] = None


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


def _check_plan_ownership(db: Session, plan_id: int, user: User):
    """检查计划是否属于当前用户。"""
    plan = db.query(LearningPlan).filter(
        LearningPlan.id == plan_id,
        LearningPlan.user_id == user.id,
    ).first()
    if not plan:
        raise HTTPException(403, "无权访问该计划")
    return plan


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
def list_reminders(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """获取某计划的提醒列表（需属于当前用户）。"""
    user = current_user or _get_or_create_guest_user(db)
    _check_plan_ownership(db, plan_id, user)
    return db.query(Reminder).filter(Reminder.plan_id == plan_id).all()


@router.post("/plan/{plan_id}")
def add_reminder(
    plan_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """为某计划添加提醒（需属于当前用户）。"""
    user = current_user or _get_or_create_guest_user(db)
    _check_plan_ownership(db, plan_id, user)

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
def toggle_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """切换提醒开关（需属于当前用户的计划）。"""
    user = current_user or _get_or_create_guest_user(db)
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    
    # 检查提醒所属计划是否属于当前用户
    _check_plan_ownership(db, reminder.plan_id, user)
    
    reminder.enabled = not reminder.enabled
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """删除提醒（需属于当前用户的计划）。"""
    user = current_user or _get_or_create_guest_user(db)
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(404, "Reminder not found")
    
    # 检查提醒所属计划是否属于当前用户
    _check_plan_ownership(db, reminder.plan_id, user)
    
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
