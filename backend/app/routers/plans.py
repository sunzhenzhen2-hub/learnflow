"""Plans router - learning plan CRUD and wizard."""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LearningPlan, LearningStep, Milestone
from ..schemas import PlanCreate, PlanResponse, PlanWizardInput, StepResponse, MilestoneResponse

router = APIRouter()


@router.get("/", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(LearningPlan).order_by(LearningPlan.created_at.desc()).all()
    result = []
    for p in plans:
        total = db.query(LearningStep).filter(LearningStep.plan_id == p.id).count()
        done = db.query(LearningStep).filter(
            LearningStep.plan_id == p.id, LearningStep.status == "completed"
        ).count()
        progress = (done / total * 100) if total > 0 else 0
        resp = PlanResponse.model_validate(p)
        resp.progress = progress
        result.append(resp)
    return result


@router.post("/", response_model=PlanResponse)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = LearningPlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.post("/wizard", response_model=PlanResponse)
def wizard_create_plan(wizard: PlanWizardInput, db: Session = Depends(get_db)):
    """Wizard-style plan creation: generates full plan from user inputs."""
    from ..services.plan_engine import generate_learning_plan

    # Create the plan
    db_plan = LearningPlan(
        topic=wizard.topic,
        goal=wizard.goal,
        current_level=wizard.current_level,
        weekly_hours=wizard.weekly_hours,
        total_weeks=16,
    )
    db.add(db_plan)
    db.flush()

    # Generate steps using the plan engine
    plan_data = generate_learning_plan(
        topic=wizard.topic,
        goal=wizard.goal,
        level=wizard.current_level,
        weekly_hours=wizard.weekly_hours,
        preferred_days=wizard.preferred_days,
        start_date=wizard.start_date or date.today(),
        focus_areas=wizard.focus_areas,
    )

    # Create steps
    for step_data in plan_data["steps"]:
        step = LearningStep(
            plan_id=db_plan.id,
            week_num=step_data["week_num"],
            day_of_week=step_data["day_of_week"],
            date=step_data["date"],
            step_type=step_data["step_type"],
            title=step_data["title"],
            content=step_data.get("content", ""),
            resources=step_data.get("resources"),
            core_20_percent=step_data.get("core_20_percent"),
            test_question=step_data.get("test_question"),
            test_answer_hint=step_data.get("test_answer_hint"),
            duration_minutes=step_data.get("duration_minutes", 60),
            ladder_level=step_data.get("ladder_level"),
            ladder_name=step_data.get("ladder_name"),
            status="available" if step_data["week_num"] == 1 else "locked",
            locked=step_data["week_num"] != 1,
        )
        db.add(step)

    # Create milestones
    for ms_data in plan_data["milestones"]:
        ms = Milestone(
            plan_id=db_plan.id,
            week_num=ms_data["week_num"],
            title=ms_data["title"],
            description=ms_data.get("description", ""),
            check_task=ms_data.get("check_task", ""),
        )
        db.add(ms)

    db_plan.total_weeks = plan_data.get("total_weeks", 16)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")
    total = db.query(LearningStep).filter(LearningStep.plan_id == plan_id).count()
    done = db.query(LearningStep).filter(
        LearningStep.plan_id == plan_id, LearningStep.status == "completed"
    ).count()
    progress = (done / total * 100) if total > 0 else 0
    resp = PlanResponse.model_validate(plan)
    resp.progress = progress
    return resp


@router.get("/{plan_id}/steps", response_model=list[StepResponse])
def get_plan_steps(plan_id: int, week: int = None, db: Session = Depends(get_db)):
    q = db.query(LearningStep).filter(LearningStep.plan_id == plan_id)
    if week:
        q = q.filter(LearningStep.week_num == week)
    return q.order_by(LearningStep.date).all()


@router.get("/{plan_id}/milestones", response_model=list[MilestoneResponse])
def get_plan_milestones(plan_id: int, db: Session = Depends(get_db)):
    return db.query(Milestone).filter(Milestone.plan_id == plan_id).order_by(Milestone.week_num).all()


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")
    db.delete(plan)
    db.commit()
    return {"ok": True}
