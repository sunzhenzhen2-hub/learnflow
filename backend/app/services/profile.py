"""Profile service - 个人学习统计聚合。"""
from datetime import date, timedelta
from sqlalchemy import func
from ..database import SessionLocal
from ..models import LearningPlan, LearningStep, Achievement


def get_profile_data() -> dict:
    """获取个人学习统计数据。"""
    db = SessionLocal()
    try:
        # 总计划数
        total_plans = db.query(LearningPlan).count()

        # 活跃计划
        active_plans = db.query(LearningPlan).filter(
            LearningPlan.status == "active"
        ).count()

        # 已完成计划
        completed_plans = db.query(LearningPlan).filter(
            LearningPlan.status == "completed"
        ).count()

        # 总步骤数
        total_steps = db.query(LearningStep).count()

        # 已完成步骤数
        completed_steps = db.query(LearningStep).filter(
            LearningStep.status == "completed"
        ).count()

        # 学习总时长（分钟）- 只计算已完成的步骤
        total_minutes = db.query(
            func.sum(LearningStep.duration_minutes)
        ).filter(
            LearningStep.status == "completed"
        ).scalar() or 0

        # 总成就数
        total_achievements = db.query(Achievement).count()

        # 各稀有度成就数
        rarity_counts = {}
        for rarity in ["common", "rare", "epic", "legendary"]:
            count = db.query(Achievement).filter(
                Achievement.rarity == rarity
            ).count()
            if count > 0:
                rarity_counts[rarity] = count

        # 最近完成的步骤（最近5个）
        recent_completed = db.query(LearningStep).filter(
            LearningStep.status == "completed"
        ).order_by(LearningStep.completed_at.desc()).limit(5).all()

        # 当前连续天数（所有计划中）
        streak = _calculate_global_streak(db)

        # 各计划进度
        plans_progress = []
        plans = db.query(LearningPlan).order_by(LearningPlan.created_at.desc()).limit(5).all()
        for plan in plans:
            plan_steps = db.query(LearningStep).filter(LearningStep.plan_id == plan.id).count()
            plan_done = db.query(LearningStep).filter(
                LearningStep.plan_id == plan.id,
                LearningStep.status == "completed"
            ).count()
            progress = (plan_done / plan_steps * 100) if plan_steps > 0 else 0
            plans_progress.append({
                "id": plan.id,
                "topic": plan.topic,
                "status": plan.status,
                "progress": round(progress, 1),
                "total_steps": plan_steps,
                "completed_steps": plan_done,
            })

        return {
            "total_plans": total_plans,
            "active_plans": active_plans,
            "completed_plans": completed_plans,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "total_achievements": total_achievements,
            "rarity_counts": rarity_counts,
            "streak_days": streak,
            "recent_completed": [
                {
                    "id": s.id,
                    "title": s.title,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                    "ai_score": s.ai_score,
                }
                for s in recent_completed
            ],
            "plans_progress": plans_progress,
        }
    finally:
        db.close()


def _calculate_global_streak(db) -> int:
    """计算全局连续完成天数（跨所有计划）。"""
    today = date.today()
    streak = 0
    check_date = today

    while True:
        completed = db.query(LearningStep).filter(
            LearningStep.date == check_date,
            LearningStep.status == "completed",
        ).first()
        if completed:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak
