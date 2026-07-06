"""LLM Config router - 外部 LLM 配置管理。"""
import httpx
from fastapi import APIRouter
from ..config import settings
from ..schemas import LLMConfigUpdate, LLMConfigResponse

router = APIRouter()

NOTIFICATION_CONFIG_KEYS = {
    'dingtalk': ['app_key', 'app_secret', 'agent_id', 'robot_code'],
    'feishu': ['app_id', 'app_secret'],
}


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


@router.post("/llm-config/test")
def test_llm_config():
    """测试 LLM 配置是否有效。"""
    if not settings.LLM_API_BASE or not settings.LLM_API_KEY:
        return {"ok": False, "message": "请先配置 API Base 和 API Key"}

    headers = {"Content-Type": "application/json"}
    if settings.LLM_API_KEY.startswith("tp-"):
        headers["api-key"] = settings.LLM_API_KEY
    else:
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"

    try:
        response = httpx.post(
            f"{settings.LLM_API_BASE}/chat/completions",
            headers=headers,
            json={
                "model": settings.LLM_MODEL,
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 100,
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return {"ok": True, "message": "配置有效", "response": content}
    except Exception as e:
        return {"ok": False, "message": f"测试失败: {str(e)}"}


@router.get("/notification-config/{channel}")
def get_notification_config(channel: str):
    """获取通知渠道配置。"""
    if channel not in NOTIFICATION_CONFIG_KEYS:
        return {"ok": False, "message": "Unknown channel"}
    
    config = {}
    for key in NOTIFICATION_CONFIG_KEYS[channel]:
        value = getattr(settings, f"{channel.upper()}_{key.upper()}", "")
        if value and not key.endswith('_secret'):
            config[key] = value
    
    return {"ok": True, "data": config}


@router.put("/notification-config/{channel}")
def save_notification_config(channel: str, config: dict):
    """保存通知渠道配置。"""
    if channel not in NOTIFICATION_CONFIG_KEYS:
        return {"ok": False, "message": "Unknown channel"}
    
    for key in NOTIFICATION_CONFIG_KEYS[channel]:
        if key in config:
            setattr(settings, f"{channel.upper()}_{key.upper()}", config[key])
    
    from pathlib import Path
    env_path = Path(__file__).parent.parent / ".env"
    with open(env_path, "a") as f:
        for key in NOTIFICATION_CONFIG_KEYS[channel]:
            if key in config:
                f.write(f"{channel.upper()}_{key.upper()}={config[key]}\n")
    
    return {"ok": True, "message": f"{channel} 配置已更新"}
