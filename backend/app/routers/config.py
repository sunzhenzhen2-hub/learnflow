"""LLM Config router - 外部 LLM 配置管理。"""
from fastapi import APIRouter, HTTPException
from ..config import settings
from ..schemas import (
    LLMConfigUpdate, LLMConfigResponse,
    LLMModelInfo, LLMModelsResponse,
)

router = APIRouter()

# 预置常用模型列表
PRESET_MODELS = [
    LLMModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="OpenAI", description="快速且经济，适合日常任务"),
    LLMModelInfo(id="gpt-4o", name="GPT-4o", provider="OpenAI", description="最强多模态模型"),
    LLMModelInfo(id="gpt-4-turbo", name="GPT-4 Turbo", provider="OpenAI", description="高性能推理"),
    LLMModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo", provider="OpenAI", description="经典快速模型"),
    LLMModelInfo(id="mimo-v2.5", name="MiMo V2.5", provider="XiaomiMiMo", description="小米推理模型，中文能力强"),
    LLMModelInfo(id="deepseek-chat", name="DeepSeek Chat", provider="DeepSeek", description="高性价比中文模型"),
    LLMModelInfo(id="deepseek-reasoner", name="DeepSeek Reasoner", provider="DeepSeek", description="深度推理模型"),
    LLMModelInfo(id="qwen-turbo", name="Qwen Turbo", provider="Alibaba", description="通义千问快速版"),
    LLMModelInfo(id="qwen-plus", name="Qwen Plus", provider="Alibaba", description="通义千问增强版"),
    LLMModelInfo(id="glm-4", name="GLM-4", provider="Zhipu", description="智谱 GLM-4，中文理解优秀"),
    LLMModelInfo(id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet", provider="Anthropic", description="Anthropic 旗舰模型"),
    LLMModelInfo(id="moonshot-v1-8k", name="Moonshot V1 8K", provider="Moonshot", description="月之暗面，长文本处理"),
]


@router.get("/llm-config", response_model=LLMConfigResponse)
def get_llm_config():
    """获取当前 LLM 配置（不返回完整 API Key）。"""
    default_model = settings.DEFAULT_MODEL or ""
    current_model = settings.LLM_MODEL
    has_key = bool(settings.LLM_API_KEY)
    configured = has_key and current_model != "gpt-4o-mini"

    return LLMConfigResponse(
        api_base=settings.LLM_API_BASE,
        model=current_model,
        default_model=default_model if default_model else current_model,
        has_key=has_key,
        configured=configured,
    )


@router.put("/llm-config")
def update_llm_config(config: LLMConfigUpdate):
    """更新 LLM 配置（运行时生效）。api_key 为空时保留原值。"""
    settings.LLM_API_BASE = config.api_base
    settings.LLM_MODEL = config.model

    # 指定默认模型
    if config.default_model:
        settings.DEFAULT_MODEL = config.default_model
    else:
        settings.DEFAULT_MODEL = config.model

    # 仅在提供了新 key 时才更新，避免误清空
    if config.api_key:
        settings.LLM_API_KEY = config.api_key

    # 写入 .env 文件持久化（合并写入，不覆盖其他配置）
    _persist_env()

    return {"ok": True, "message": "LLM 配置已更新"}


@router.get("/llm-models", response_model=LLMModelsResponse)
def list_models():
    """获取可用模型列表及当前配置。"""
    return LLMModelsResponse(
        current_model=settings.LLM_MODEL,
        default_model=settings.DEFAULT_MODEL or settings.LLM_MODEL,
        models=PRESET_MODELS,
    )


@router.post("/llm-config/test")
def test_llm_config():
    """测试 LLM API 连通性，发送一个简单请求。"""
    import httpx

    if not settings.LLM_API_KEY:
        raise HTTPException(status_code=400, detail="API Key 未配置")

    url = f"{settings.LLM_API_BASE}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5,
    }
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(url, json=payload, headers=headers)

        if resp.status_code == 200:
            data = resp.json()
            model_used = data.get("model", settings.LLM_MODEL)
            return {
                "success": True,
                "message": f"连接成功，模型 {model_used} 响应正常",
                "model": model_used,
            }
        else:
            error_msg = resp.text[:200]
            return {
                "success": False,
                "message": f"API 返回错误 (HTTP {resp.status_code}): {error_msg}",
            }
    except httpx.ConnectError:
        return {"success": False, "message": f"无法连接到 {settings.LLM_API_BASE}，请检查 API 地址"}
    except httpx.TimeoutException:
        return {"success": False, "message": "请求超时，请检查网络连接"}
    except Exception as e:
        return {"success": False, "message": f"测试失败: {str(e)[:200]}"}


def _persist_env():
    """将 LLM 配置合并写入 .env，保留其他已有配置项。"""
    from pathlib import Path

    env_path = Path(__file__).parent.parent / ".env"
    existing = {}

    # 读取已有配置
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                existing[key.strip()] = value.strip()

    # 更新 LLM 相关配置
    existing["LLM_API_BASE"] = settings.LLM_API_BASE
    existing["LLM_API_KEY"] = settings.LLM_API_KEY
    existing["LLM_MODEL"] = settings.LLM_MODEL
    if settings.DEFAULT_MODEL:
        existing["DEFAULT_MODEL"] = settings.DEFAULT_MODEL

    # 写回文件
    with open(env_path, "w", encoding="utf-8") as f:
        for key, value in existing.items():
            f.write(f"{key}={value}\n")
