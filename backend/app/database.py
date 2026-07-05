"""Database setup with SQLite."""
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings

engine = create_engine(
    f"sqlite:///{settings.DB_PATH}",
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_columns()


def _migrate_columns():
    """Add new columns to existing tables if they don't exist yet."""
    inspector = inspect(engine)
    existing_columns = {col["name"] for col in inspector.get_columns("learning_steps")}

    new_columns = [
        ("core_20_percent", "TEXT"),
        ("ladder_level", "INTEGER"),
        ("ladder_name", "VARCHAR(50)"),
    ]

    with engine.connect() as conn:
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE learning_steps ADD COLUMN {col_name} {col_type}"))
                conn.commit()
