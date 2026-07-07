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

    # Migrate learning_steps
    steps_columns = {col["name"] for col in inspector.get_columns("learning_steps")}
    steps_new_columns = [
        ("core_20_percent", "TEXT"),
        ("ladder_level", "INTEGER"),
        ("ladder_name", "VARCHAR(50)"),
        ("doc_content", "TEXT"),
    ]
    with engine.connect() as conn:
        for col_name, col_type in steps_new_columns:
            if col_name not in steps_columns:
                conn.execute(text(f"ALTER TABLE learning_steps ADD COLUMN {col_name} {col_type}"))
                conn.commit()

    # Migrate learning_plans: add user_id
    plans_columns = {col["name"] for col in inspector.get_columns("learning_plans")}
    if "user_id" not in plans_columns:
        with engine.connect() as conn:
            # Create temporary users table if not exists (for migration)
            existing_tables = inspector.get_table_names()
            if "users" not in existing_tables:
                conn.execute(text("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        is_admin BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME,
                        must_change_password BOOLEAN DEFAULT 0
                    )
                """))
                conn.commit()

            conn.execute(text("ALTER TABLE learning_plans ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            conn.commit()

            # Migrate existing plans to a default guest user (id=1)
            conn.execute(text("UPDATE learning_plans SET user_id = 1 WHERE user_id IS NULL"))
            conn.commit()

    # Create user_sessions table
    existing_tables = inspector.get_table_names()
    if "user_sessions" not in existing_tables:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    login_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    logout_at DATETIME,
                    ip_address VARCHAR(50),
                    user_agent VARCHAR(500),
                    token VARCHAR(500)
                )
            """))
            conn.commit()
