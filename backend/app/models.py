"""SQLAlchemy models."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    must_change_password = Column(Boolean, default=False)

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    plans = relationship("LearningPlan", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_at = Column(DateTime, default=datetime.utcnow)
    logout_at = Column(DateTime, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    token = Column(String(500), nullable=True)  # JWT token hash for reference

    user = relationship("User", back_populates="sessions")


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic = Column(String(200), nullable=False)
    goal = Column(Text, nullable=False)
    current_level = Column(String(50), nullable=False)
    weekly_hours = Column(Float, default=10.0)
    total_weeks = Column(Integer, default=16)
    status = Column(String(20), default="active")  # active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    steps = relationship("LearningStep", back_populates="plan", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="plan", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="plan", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="plan", cascade="all, delete-orphan")


class LearningStep(Base):
    __tablename__ = "learning_steps"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("learning_plans.id"), nullable=False)
    week_num = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=Mon..7=Sun
    date = Column(Date, nullable=False)
    step_type = Column(String(20), nullable=False)  # study, project, output, cheat_sheet, test
    title = Column(String(200), nullable=False)
    content = Column(Text)  # 中文学习内容
    doc_content = Column(Text)  # 文档内容（独立存储）
    resources = Column(JSON)  # 学习资源列表 [{"type":"video","title":"","url":"","platform":"","level":"","duration":"","why":""}, ...]
    core_20_percent = Column(Text)  # 二八法则：本周核心20%内容
    test_questions = Column(JSON, nullable=True)  # 结构化测试题 JSON：[{"type":"choice"|"true_false"|"short", "question":"...","options":[...],"correct":"A","keywords":[...]}]]
    test_answer_hint = Column(Text)  # 测试答案提示（用于AI评分参考）
    duration_minutes = Column(Integer, default=60)
    ladder_level = Column(Integer)  # 学习阶梯等级（1-5）
    ladder_name = Column(String(50))  # 学习阶梯等级名称
    status = Column(String(20), default="locked")  # locked, available, in_progress, review_passed, completed
    locked = Column(Boolean, default=True)
    output_content = Column(Text)  # 用户输出/测试答案
    ai_review_result = Column(JSON)  # AI评审反馈（含苏格拉底追问、费曼评分、速查表建议）
    ai_score = Column(Float)  # AI评审分数(0-100)
    completed_at = Column(DateTime)

    plan = relationship("LearningPlan", back_populates="steps")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("learning_plans.id"), nullable=False)
    week_num = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    check_task = Column(Text)  # 费曼检查任务
    status = Column(String(20), default="pending")  # pending, in_progress, completed

    plan = relationship("LearningPlan", back_populates="milestones")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("learning_plans.id"), nullable=False)
    channel = Column(String(20), nullable=False)  # feishu, dingtalk, windows
    channel_config = Column(JSON)  # 通道配置
    enabled = Column(Boolean, default=True)
    last_sent_at = Column(DateTime)

    plan = relationship("LearningPlan", back_populates="reminders")


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("learning_plans.id"), nullable=False)
    badge_key = Column(String(50), nullable=False)  # 成就标识: first_step, week_streak_7, milestone, perfect_score, etc.
    title = Column(String(200), nullable=False)  # 成就标题
    description = Column(Text)  # 成就描述
    icon = Column(String(50), default="Trophy")  # 图标名
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("LearningPlan", back_populates="achievements")
