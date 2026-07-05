"""Pydantic schemas for API."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# --- Plan Schemas ---
class PlanCreate(BaseModel):
    topic: str
    goal: str
    current_level: str
    weekly_hours: float = 10.0
    total_weeks: int = 16


class PlanResponse(BaseModel):
    id: int
    topic: str
    goal: str
    current_level: str
    weekly_hours: float
    total_weeks: int
    status: str
    created_at: datetime
    progress: float = 0.0

    class Config:
        from_attributes = True


class PlanWizardInput(BaseModel):
    """向导式计划创建输入。"""
    topic: str
    goal: str
    current_level: str
    weekly_hours: float
    preferred_days: list[int] = [1, 3, 5, 6, 7]
    start_date: Optional[date] = None
    focus_areas: list[str] = []


# --- Step Schemas ---
class StepResponse(BaseModel):
    id: int
    plan_id: int
    week_num: int
    day_of_week: int
    date: date
    step_type: str
    title: str
    content: Optional[str]
    resources: Optional[list[dict]] = None
    core_20_percent: Optional[str] = None
    test_question: Optional[str] = None
    duration_minutes: int
    ladder_level: Optional[int] = None
    ladder_name: Optional[str] = None
    status: str
    locked: bool
    output_content: Optional[str]
    ai_review_result: Optional[dict]
    ai_score: Optional[float]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class StepOutputSubmit(BaseModel):
    """用户提交学习输出/测试答案。"""
    content: str


class StepReviewResult(BaseModel):
    step_id: int
    passed: bool
    score: float
    feedback: str
    suggestions: list[str]
    socratic_question: Optional[str] = None
    feynman_score: Optional[int] = None
    feynman_analysis: Optional[dict] = None
    cheat_sheet: Optional[str] = None


# --- Milestone Schemas ---
class MilestoneResponse(BaseModel):
    id: int
    plan_id: int
    week_num: int
    title: str
    description: Optional[str]
    check_task: Optional[str]
    status: str

    class Config:
        from_attributes = True


# --- Reminder Schemas ---
class ReminderCreate(BaseModel):
    channel: str
    channel_config: dict = {}
    enabled: bool = True


class ReminderResponse(BaseModel):
    id: int
    plan_id: int
    channel: str
    channel_config: dict
    enabled: bool
    last_sent_at: Optional[datetime]

    class Config:
        from_attributes = True


# --- Achievement Schemas ---
class AchievementResponse(BaseModel):
    id: int
    plan_id: int
    badge_key: str
    title: str
    description: Optional[str]
    icon: str
    rarity: str
    unlocked_at: datetime

    class Config:
        from_attributes = True


# --- LLM Config Schema ---
class LLMConfigUpdate(BaseModel):
    api_base: str
    api_key: str
    model: str


class LLMConfigResponse(BaseModel):
    api_base: str
    model: str
    has_key: bool


# --- Dashboard Schema ---
class DashboardData(BaseModel):
    active_plan: Optional[PlanResponse]
    today_step: Optional[StepResponse]
    upcoming_steps: list[StepResponse]
    milestones: list[MilestoneResponse]
    achievements: list[AchievementResponse]
    streak_days: int
    total_completed: int
    total_steps: int
