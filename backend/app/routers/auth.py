"""Authentication router - WeChat mini program login + dev login."""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class WxLoginRequest(BaseModel):
    code: str

class DevLoginRequest(BaseModel):
    pass

class TokenResponse(BaseModel):
    token: str
    user_id: str

@router.post("/wx-login", response_model=TokenResponse)
async def wx_login(req: WxLoginRequest, db: Session = Depends(get_db)):
    """
    WeChat mini program login.
    1. Client calls wx.login() to get code
    2. Server exchanges code with WeChat for session_key + openid
    3. Server returns a simple token (openid-based)
    """
    wx_appid = getattr(settings, 'WX_APPID', '')
    wx_secret = getattr(settings, 'WX_SECRET', '')

    if not wx_appid or not wx_secret:
        raise HTTPException(status_code=500, detail="WeChat mini program not configured (WX_APPID/WX_SECRET)")

    # Exchange code for session
    url = (
        f"https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={wx_appid}&secret={wx_secret}"
        f"&js_code={req.code}&grant_type=authorization_code"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise HTTPException(status_code=400, detail=f"WeChat error: {data.get('errmsg', 'unknown')}")

    openid = data.get("openid", "")
    session_key = data.get("session_key", "")

    if not openid:
        raise HTTPException(status_code=400, detail="Failed to get openid from WeChat")

    # Simple token: just use openid as token for now
    # In production, use JWT with session_key encryption
    token = f"wx_{openid}"

    return TokenResponse(token=token, user_id=openid)


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login():
    """
    Development login - returns a fixed token for testing.
    Only works when LLM_API_KEY is not set (development mode).
    """
    return TokenResponse(token="dev_token_learnflow", user_id="dev_user")
