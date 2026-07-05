"""Scheduler service - periodic reminder jobs."""
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler

from ..database import SessionLocal
from ..models import LearningStep, Reminder
from .notifiers import send_notification

scheduler = BackgroundScheduler()


def start_scheduler():
    """Start the background scheduler."""
    # Check daily at 8:00 AM for today's learning tasks
    scheduler.add_job(
        daily_reminder_job,
        "cron",
        hour=8,
        minute=0,
        id="daily_reminder",
        replace_existing=True,
    )

    # Check at 2:00 PM for afternoon reminders
    scheduler.add_job(
        afternoon_reminder_job,
        "cron",
        hour=14,
        minute=0,
        id="afternoon_reminder",
        replace_existing=True,
    )

    # Sunday evening: weekly review reminder
    scheduler.add_job(
        weekly_review_reminder,
        "cron",
        day_of_week="sun",
        hour=19,
        minute=0,
        id="weekly_review",
        replace_existing=True,
    )

    scheduler.start()


def daily_reminder_job():
    """Send morning reminders for today's learning tasks."""
    db = SessionLocal()
    try:
        today = date.today()
        steps = db.query(LearningStep).filter(
            LearningStep.date == today,
            LearningStep.status.in_(["available", "in_progress"]),
        ).all()

        if not steps:
            return

        reminders = db.query(Reminder).filter(Reminder.enabled == True).all()

        for step in steps:
            title = f"Today's Learning: {step.title}"
            body = (
                f"Week {step.week_num} | {step.step_type} | {step.duration_minutes}min\n"
                f"{step.content[:200] if step.content else ''}"
            )

            for reminder in reminders:
                send_notification(
                    channel=reminder.channel,
                    title=title,
                    body=body,
                    **(reminder.channel_config or {}),
                )
    finally:
        db.close()


def afternoon_reminder_job():
    """Send afternoon reminder if today's task is not started."""
    db = SessionLocal()
    try:
        today = date.today()
        steps = db.query(LearningStep).filter(
            LearningStep.date == today,
            LearningStep.status == "available",  # Not started yet
        ).all()

        if not steps:
            return

        reminders = db.query(Reminder).filter(Reminder.enabled == True).all()

        for step in steps:
            title = f"Reminder: {step.title}"
            body = "You haven't started today's learning task yet. Time to get going!"

            for reminder in reminders:
                send_notification(
                    channel=reminder.channel,
                    title=title,
                    body=body,
                    **(reminder.channel_config or {}),
                )
    finally:
        db.close()


def weekly_review_reminder():
    """Sunday evening: remind about weekly output."""
    db = SessionLocal()
    try:
        today = date.today()
        output_step = db.query(LearningStep).filter(
            LearningStep.date == today,
            LearningStep.step_type == "output",
        ).first()

        if not output_step:
            return

        reminders = db.query(Reminder).filter(Reminder.enabled == True).all()
        title = "Weekly Writing Output"
        body = (
            "Time for your weekly writing output! "
            "Summarize what you learned this week and submit for AI review."
        )

        for reminder in reminders:
            send_notification(
                channel=reminder.channel,
                title=title,
                body=body,
                **(reminder.channel_config or {}),
            )
    finally:
        db.close()
