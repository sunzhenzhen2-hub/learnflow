"""WeChat subscription message service.

Sends learning reminders via WeChat mini program subscription messages.
Requires WX_APPID and WX_SECRET configured in .env.

Flow:
1. User enables notifications in mini app settings
2. User grants permission via wx.requestSubscribeMessage()
3. Backend sends subscription message via WeChat API
"""
import time
import httpx
from typing import Optional, Dict
from ..config import settings

# Cache for access_token (valid 2 hours, refresh at 1.5 hours)
_token_cache: Dict = {"token": "", "expires_at": 0}


async def get_access_token() -> str:
    """Get WeChat access_token, cached with auto-refresh."""
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now:
        return _token_cache["token"]

    wx_appid = getattr(settings, "WX_APPID", "")
    wx_secret = getattr(settings, "WX_SECRET", "")
    if not wx_appid or not wx_secret:
        raise ValueError("WX_APPID/WX_SECRET not configured")

    url = (
        f"https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={wx_appid}&secret={wx_secret}"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise ValueError(f"WeChat error: {data.get('errmsg', 'unknown')}")

    token = data.get("access_token", "")
    expires_in = data.get("expires_in", 7200)

    # Cache with 5-minute buffer
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + expires_in - 300

    return token


async def send_subscribe_message(
    openid: str,
    template_id: str,
    data: dict,
    page: str = "pages/dashboard/index",
) -> dict:
    """
    Send a WeChat subscription message.

    Args:
        openid: User's WeChat openid
        template_id: Message template ID (from WeChat MP console)
        data: Template data dict, e.g.:
              {"thing1": {"value": "React"}, "time2": {"value": "2026-07-06 09:00"}}
        page: Page path to navigate to when user taps the notification

    Returns:
        WeChat API response dict
    """
    token = await get_access_token()
    url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={token}"

    payload = {
        "touser": openid,
        "template_id": template_id,
        "page": page,
        "data": data,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        return resp.json()


async def send_learning_reminder(
    openid: str,
    topic: str,
    step_title: str,
    remind_time: str,
    template_id: Optional[str] = None,
) -> dict:
    """
    Send a learning reminder subscription message.

    Uses a standard template with fields:
    - thing1: Learning topic
    - thing2: Step title
    - time3: Reminder time
    """
    if not template_id:
        template_id = getattr(settings, "WX_TEMPLATE_ID", "")
    if not template_id:
        return {"errcode": -1, "errmsg": "WX_TEMPLATE_ID not configured"}

    data = {
        "thing1": {"value": topic[:20]},
        "thing2": {"value": step_title[:20]},
        "time3": {"value": remind_time},
    }

    return await send_subscribe_message(
        openid=openid,
        template_id=template_id,
        data=data,
        page="pages/learn/index",
    )
