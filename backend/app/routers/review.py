"""Review router - AI评审用户输出（Skill 深度嵌入版）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LearningStep, LearningPlan, User
from ..schemas import StepReviewResult, StepOutputSubmit
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


def _check_step_ownership(db: Session, step_id: int, user: User):
    """检查步骤是否属于当前用户。"""
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")
    plan = db.query(LearningPlan).filter(
        LearningPlan.id == step.plan_id,
        LearningPlan.user_id == user.id,
    ).first()
    if not plan:
        raise HTTPException(403, "无权访问该步骤")
    return step


@router.post("/{step_id}/review", response_model=StepReviewResult)
def review_output(
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """AI评审用户提交的学习输出/测试答案（需属于当前用户）。"""
    user = current_user or _get_or_create_guest_user(db)
    step = _check_step_ownership(db, step_id, user)
    
    if not step.output_content:
        raise HTTPException(400, "尚未提交输出")

    from ..services.reviewer import review_learning_output

    result = review_learning_output(
        step_title=step.title,
        step_content=step.content or "",
        user_output=step.output_content,
        step_type=step.step_type,
        test_question=step.test_question or "",
        test_answer_hint=step.test_answer_hint or "",
        ladder_level=step.ladder_level or "",
        ladder_name=step.ladder_name or "",
    )

    step.ai_review_result = {
        "feedback": result["feedback"],
        "suggestions": result["suggestions"],
        "socratic_question": result.get("socratic_question", ""),
        "feynman_score": result.get("feynman_score"),
        "feynman_analysis": result.get("feynman_analysis"),
        "cheat_sheet": result.get("cheat_sheet"),
    }
    step.ai_score = result["score"]

    if result["passed"]:
        step.status = "review_passed"

    db.commit()

    return StepReviewResult(
        step_id=step_id,
        passed=result["passed"],
        score=result["score"],
        feedback=result["feedback"],
        suggestions=result["suggestions"],
        socratic_question=result.get("socratic_question"),
        feynman_score=result.get("feynman_score"),
        feynman_analysis=result.get("feynman_analysis"),
        cheat_sheet=result.get("cheat_sheet"),
    )


@router.post("/{step_id}/review-retry")
def retry_output(
    step_id: int,
    output: StepOutputSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """用户根据反馈修改后重新提交（需属于当前用户）。"""
    user = current_user or _get_or_create_guest_user(db)
    step = _check_step_ownership(db, step_id, user)

    step.output_content = output.content
    step.ai_review_result = None
    step.ai_score = None
    step.status = "in_progress"
    db.commit()
    return {"ok": True, "message": "输出已更新，请重新提交评审。"}


@router.post("/{step_id}/test-grade")
def grade_test(
    step_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """AI评分测试题（需属于当前用户）。"""
    user = current_user or _get_or_create_guest_user(db)
    step = _check_step_ownership(db, step_id, user)
    
    from ..schemas import StepTestSubmit
    from ..services.reviewer import grade_test_questions
    import json

    body["step_id"] = step_id
    submit = StepTestSubmit(**body)
    
    test_questions = step.test_questions or []
    if not test_questions:
        raise HTTPException(400, "no test questions")
    
    # Convert Pydantic objects to dicts for grade_test_questions
    answers_dict = [{"question_index": a.question_index, "answer": a.answer} for a in submit.answers]
    result = grade_test_questions(test_questions, answers_dict)
    
    step.ai_score = result["score"]
    step.ai_review_result = {
        "feedback": result["feedback"],
        "suggestions": result["suggestions"],
        "test_results": result["results"],
    }
    step.output_content = json.dumps(answers_dict, ensure_ascii=False)
    
    if result["passed"]:
        step.status = "review_passed"
    
    db.commit()
    
    return {
        "step_id": step_id,
        "passed": result["passed"],
        "score": result["score"],
        "total": result["total"],
        "correct": result["correct"],
        "results": result["results"],
        "feedback": result["feedback"],
        "suggestions": result["suggestions"],
    }
