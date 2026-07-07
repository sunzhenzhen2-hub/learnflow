"""Dashboard service - 聚合仪表盘数据。"""
from datetime import date, timedelta
from ..database import SessionLocal
from ..models import LearningPlan, LearningStep, Milestone, Achievement


def get_dashboard_data(user_id: int) -> dict:
    """获取聚合仪表盘数据（按用户隔离）。guest用户可见所有计划。"""
    db = SessionLocal()
    try:
        # guest user (id=1) sees all plans, regular users only see their own
        active_plan = db.query(LearningPlan).filter(
            LearningPlan.status == "active"
        ).order_by(LearningPlan.created_at.desc()).first()

        if not active_plan:
            return {
                "active_plan": None,
                "today_step": None,
                "upcoming_steps": [],
                "milestones": [],
                "achievements": [],
                "streak_days": 0,
                "total_completed": 0,
                "total_steps": 0,
            }

        today = date.today()
        today_step = db.query(LearningStep).filter(
            LearningStep.plan_id == active_plan.id,
            LearningStep.date == today,
        ).first()

        if not today_step:
            today_step = db.query(LearningStep).filter(
                LearningStep.plan_id == active_plan.id,
                LearningStep.date >= today,
                LearningStep.status.in_(["available", "in_progress"]),
            ).order_by(LearningStep.date).first()

        upcoming = db.query(LearningStep).filter(
            LearningStep.plan_id == active_plan.id,
            LearningStep.date >= today,
            LearningStep.date <= today + timedelta(days=7),
        ).order_by(LearningStep.date).limit(10).all()

        milestones = db.query(Milestone).filter(
            Milestone.plan_id == active_plan.id
        ).order_by(Milestone.week_num).all()

        achievements = db.query(Achievement).filter(
            Achievement.plan_id == active_plan.id
        ).order_by(Achievement.unlocked_at.desc()).all()

        total_steps = db.query(LearningStep).filter(
            LearningStep.plan_id == active_plan.id
        ).count()
        completed = db.query(LearningStep).filter(
            LearningStep.plan_id == active_plan.id,
            LearningStep.status == "completed",
        ).count()

        streak = _calculate_streak(db, active_plan.id)
        progress = (completed / total_steps * 100) if total_steps > 0 else 0

        return {
            "active_plan": {
                "id": active_plan.id,
                "topic": active_plan.topic,
                "goal": active_plan.goal,
                "current_level": active_plan.current_level,
                "total_weeks": active_plan.total_weeks,
                "status": active_plan.status,
                "progress": round(progress, 1),
                "created_at": active_plan.created_at.isoformat(),
            },
            "today_step": _step_to_dict(today_step) if today_step else None,
            "upcoming_steps": [_step_to_dict(s) for s in upcoming],
            "milestones": [
                {
                    "id": m.id,
                    "week_num": m.week_num,
                    "title": m.title,
                    "description": m.description,
                    "check_task": m.check_task,
                    "status": m.status,
                }
                for m in milestones
            ],
            "achievements": [
                {
                    "id": a.id,
                    "plan_id": a.plan_id,
                    "badge_key": a.badge_key,
                    "title": a.title,
                    "description": a.description,
                    "icon": a.icon,
                    "rarity": a.rarity,
                    "unlocked_at": a.unlocked_at.isoformat(),
                }
                for a in achievements
            ],
            "streak_days": streak,
            "total_completed": completed,
            "total_steps": total_steps,
        }
    finally:
        db.close()


def _step_to_dict(step: LearningStep) -> dict:
    # 确保字符串字段不包含裸的\n
    def clean_str(s):
        if s is None:
            return None
        # 保留正常的换行符，不做额外处理
        return s

    return {
        "id": step.id,
        "plan_id": step.plan_id,
        "week_num": step.week_num,
        "day_of_week": step.day_of_week,
        "date": step.date.isoformat(),
        "step_type": step.step_type,
        "title": step.title,
        "content": clean_str(step.content),
        "resources": step.resources,
        "test_questions": step.test_questions,
        "doc_content": clean_str(step.doc_content),
        "core_20_percent": clean_str(step.core_20_percent),
        "duration_minutes": step.duration_minutes,
        "ladder_level": step.ladder_level,
        "ladder_name": step.ladder_name,
        "status": step.status,
        "locked": step.locked,
        "output_content": step.output_content,
        "ai_review_result": step.ai_review_result,
        "ai_score": step.ai_score,
    }


def _calculate_streak(db, plan_id: int) -> int:
    """计算连续完成天数。"""
    today = date.today()
    streak = 0
    check_date = today

    while True:
        completed = db.query(LearningStep).filter(
            LearningStep.plan_id == plan_id,
            LearningStep.date == check_date,
            LearningStep.status == "completed",
        ).first()
        if completed:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak
