"""Review router - AI评审用户输出（Skill 深度嵌入版）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LearningStep
from ..schemas import StepReviewResult, StepOutputSubmit

router = APIRouter()


@router.post("/{step_id}/review", response_model=StepReviewResult)
def review_output(step_id: int, db: Session = Depends(get_db)):
    """AI评审用户提交的学习输出/测试答案。"""
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")
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
def retry_output(step_id: int, output: StepOutputSubmit, db: Session = Depends(get_db)):
    """用户根据反馈修改后重新提交。"""
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "步骤不存在")

    step.output_content = output.content
    step.ai_review_result = None
    step.ai_score = None
    step.status = "in_progress"
    db.commit()
    return {"ok": True, "message": "输出已更新，请重新提交评审。"}


@router.post("/{step_id}/test-grade")
def grade_test(step_id: int, body: dict, db: Session = Depends(get_db)):
    from ..schemas import StepTestSubmit
    from ..services.reviewer import grade_test_questions
    import json

    body["step_id"] = step_id
    submit = StepTestSubmit(**body)
    
    step = db.query(LearningStep).filter(LearningStep.id == step_id).first()
    if not step:
        raise HTTPException(404, "not found")
    
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
