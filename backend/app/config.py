"""LearnFlow Configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).parent.parent.parent
_BACKEND_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "LearnFlow"
    DEBUG: bool = True

    # Database
    DB_PATH: str = str(_BASE_DIR / "data" / "learnflow.db")

    # LLM API (for content generation and review)
    LLM_API_BASE: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    DEFAULT_MODEL: str = ""  # 用户指定的默认模型，为空时使用 LLM_MODEL

    # Feishu (via lark-cli)
    FEISHU_ENABLED: bool = False

    # DingTalk (via dws)
    DINGTALK_ENABLED: bool = False

    # WeChat Mini Program
    WX_APPID: str = ""
    WX_SECRET: str = ""
    WX_TEMPLATE_ID: str = ""  # Subscription message template ID

    # Windows toast notifications
    WINDOWS_NOTIFY_ENABLED: bool = True


settings = Settings()


def effective_model() -> str:
    """返回实际使用的模型：优先使用 DEFAULT_MODEL，否则使用 LLM_MODEL。"""
    return settings.DEFAULT_MODEL if settings.DEFAULT_MODEL else settings.LLM_MODEL


# Ensure data directory exists
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
