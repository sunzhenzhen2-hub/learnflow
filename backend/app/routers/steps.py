"""Steps router - 管理学习步骤（含强制输出解锁机制）。"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LearningStep, Achievement, Milestone
from ..schemas import StepResponse, StepOutputSubmit

router = APIRouter()


@router.get("/today", response_model=StepResponse | None)
def get_today_step(db: Session = Depends(get_db)):
    """获取今日学习步骤。"""
    from datetime import date
    today = date.today()
    step = db.query(LearningStep).filter(
        LearningStep.date == today,
        LearningStep.status.in_(["available", "in_progress"])
    ).first()
    if not step:
        step = db.query(LearningStep).filter(
            LearningStep.date >= today,
            LearningStep.status.in_(["available", "in_progress"])
        ).order_by(LearningStep.date).first()
    return step


@router.get("/{step_id}", response_model=StepResponse)
def get_step(step_id: int, db: Session = Depends(get_db)):
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")
    return step


@router.post("/{step_id}/start", response_model=StepResponse)
def start_step(step_id: int, db: Session = Depends(get_db)):
    """开始学习步骤。"""
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")
    if step.locked:
        raise HTTPException(403, "步骤已锁定，请先完成前面的步骤。")
    step.status = "in_progress"
    db.commit()
    db.refresh(step)
    return step


@router.post("/{step_id}/submit-output", response_model=StepResponse)
def submit_output(step_id: int, output: StepOutputSubmit, db: Session = Depends(get_db)):
    """提交学习输出/测试答案，等待AI评审。"""
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")
    if step.status != "in_progress":
        raise HTTPException(400, "步骤未在进行中")

    step.output_content = output.content
    db.commit()
    db.refresh(step)
    return step


@router.post("/{step_id}/complete", response_model=StepResponse)
def complete_step(step_id: int, db: Session = Depends(get_db)):
    """完成步骤并解锁下一步（强制输出门控）。"""
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")

    # --- 强制输出门控：必须通过 AI 评审（>=70分）---
    if not step.output_content:
        raise HTTPException(403, "请先提交你的学习输出才能完成此步骤。")
    if step.ai_score is None or step.ai_score < 70:
        raise HTTPException(403, f"AI评审分数为 {step.ai_score or 0}/100，需要至少70分才能继续。请修改输出后重新提交。")

    step.status = "completed"
    step.completed_at = datetime.utcnow()
    step.locked = True

    # 解锁同周的下一个步骤
    next_steps = db.query(LearningStep).filter(
        LearningStep.plan_id == step.plan_id,
        LearningStep.week_num == step.week_num,
        LearningStep.status == "locked"
    ).order_by(LearningStep.date).all()

    if next_steps:
        next_steps[0].locked = False
        next_steps[0].status = "available"

    # 如果本周所有步骤都完成了，解锁下周第一个步骤
    week_completed = db.query(LearningStep).filter(
        LearningStep.plan_id == step.plan_id,
        LearningStep.week_num == step.week_num,
        LearningStep.status == "completed"
    ).count()
    total_in_week = db.query(LearningStep).filter(
        LearningStep.plan_id == step.plan_id,
        LearningStep.week_num == step.week_num,
    ).count()

    if week_completed == total_in_week:
        next_week_steps = db.query(LearningStep).filter(
            LearningStep.plan_id == step.plan_id,
            LearningStep.week_num == step.week_num + 1,
            LearningStep.status == "locked"
        ).order_by(LearningStep.date).all()
        if next_week_steps:
            next_week_steps[0].locked = False
            next_week_steps[0].status = "available"

    db.commit()
    db.refresh(step)

    # 检查并解锁成就
    _check_achievements(db, step.plan_id)

    return step


def _check_achievements(db: Session, plan_id: int):
    """检查并解锁成就（Keep 式成就体系）。"""
    total_steps = db.query(LearningStep).filter(LearningStep.plan_id == plan_id).count()
    completed = db.query(LearningStep).filter(
        LearningStep.plan_id == plan_id,
        LearningStep.status == "completed"
    ).count()
    existing = {a.badge_key for a in db.query(Achievement).filter(Achievement.plan_id == plan_id).all()}

    new_achievements = []

    # 第一步完成
    if completed >= 1 and "first_step" not in existing:
        new_achievements.append(Achievement(
            plan_id=plan_id, badge_key="first_step",
            title="迈出第一步", description="完成了第一个学习步骤",
            icon="Flag", rarity="common",
        ))

    # 连续完成 7 步
    if completed >= 7 and "streak_7" not in existing:
        new_achievements.append(Achievement(
            plan_id=plan_id, badge_key="streak_7",
            title="七日坚持", description="连续完成7个学习步骤",
            icon="Flame", rarity="rare",
        ))

    # 连续完成 30 步
    if completed >= 30 and "streak_30" not in existing:
        new_achievements.append(Achievement(
            plan_id=plan_id, badge_key="streak_30",
            title="月度达人", description="连续完成30个学习步骤",
            icon="Medal", rarity="epic",
        ))

    # 完美评分（>=95分）
    perfect = db.query(LearningStep).filter(
        LearningStep.plan_id == plan_id,
        LearningStep.ai_score >= 95,
        LearningStep.status == "completed"
    ).count()
    if perfect >= 1 and "perfect_score" not in existing:
        new_achievements.append(Achievement(
            plan_id=plan_id, badge_key="perfect_score",
            title="精益求精", description="获得一次95分以上的完美评审",
            icon="Star", rarity="rare",
        ))

    # 完成全部步骤
    if completed == total_steps and total_steps > 0 and "all_complete" not in existing:
        new_achievements.append(Achievement(
            plan_id=plan_id, badge_key="all_complete",
            title="学有所成", description="完成了整个学习计划的所有步骤",
            icon="Trophy", rarity="legendary",
        ))

    # 里程碑成就
    milestones = db.query(Milestone).filter(Milestone.plan_id == plan_id).order_by(Milestone.week_num).all()
    for ms in milestones:
        ms_key = f"milestone_w{ms.week_num}"
        if ms_key not in existing:
            week_done = db.query(LearningStep).filter(
                LearningStep.plan_id == plan_id,
                LearningStep.week_num == ms.week_num,
                LearningStep.status == "completed"
            ).count()
            week_total = db.query(LearningStep).filter(
                LearningStep.plan_id == plan_id,
                LearningStep.week_num == ms.week_num,
            ).count()
            if week_done == week_total and week_total > 0:
                new_achievements.append(Achievement(
                    plan_id=plan_id, badge_key=ms_key,
                    title=f"里程碑：{ms.title}",
                    description=ms.description,
                    icon="Trophy", rarity="epic",
                ))

    for a in new_achievements:
        db.add(a)
    if new_achievements:
        db.commit()
