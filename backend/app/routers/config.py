"""LLM Config router - 外部 LLM 配置管理。"""
from fastapi import APIRouter
from ..config import settings
from ..schemas import LLMConfigUpdate, LLMConfigResponse

router = APIRouter()


@router.get("/llm-config", response_model=LLMConfigResponse)
def get_llm_config():
    """获取当前 LLM 配置（不返回完整 API Key）。"""
    return LLMConfigResponse(
        api_base=settings.LLM_API_BASE,
        model=settings.LLM_MODEL,
        has_key=bool(settings.LLM_API_KEY),
    )


@router.put("/llm-config")
def update_llm_config(config: LLMConfigUpdate):
    """更新 LLM 配置（运行时生效）。api_key 为空时保留原值。"""
    settings.LLM_API_BASE = config.api_base
    settings.LLM_MODEL = config.model
    # 仅在提供了新 key 时才更新，避免误清空
    if config.api_key:
        settings.LLM_API_KEY = config.api_key

    # 同时写入 .env 文件持久化
    from pathlib import Path
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "w") as f:
        f.write(f"LLM_API_BASE={settings.LLM_API_BASE}\n")
        f.write(f"LLM_API_KEY={settings.LLM_API_KEY}\n")
        f.write(f"LLM_MODEL={settings.LLM_MODEL}\n")

    return {"ok": True, "message": "LLM 配置已更新"}
