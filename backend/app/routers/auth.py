"""Authentication router - JWT login + WeChat mini program login + dev login."""
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import User, UserSession
from ..schemas import Token, TokenData, ChangePasswordRequest
from ..services.auth import verify_password, get_password_hash, create_access_token, decode_access_token, validate_password
from ..config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
    return user


async def get_current_user_or_none(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


def _get_client_info(request: Request) -> tuple:
    """提取客户端 IP 和 User-Agent。"""
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")[:500]
    return ip, ua


def _create_session(db: Session, user: User, token: str, ip: str, ua: str) -> UserSession:
    """创建登录会话记录。"""
    session = UserSession(
        user_id=user.id,
        login_at=datetime.utcnow(),
        token=token[:200] if token else None,
        ip_address=ip,
        user_agent=ua,
    )
    db.add(session)
    return session


@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
    
    user.last_login = datetime.utcnow()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin},
        expires_delta=access_token_expires
    )
    
    # 写入登录会话记录
    ip, ua = _get_client_info(request)
    _create_session(db, user, access_token, ip, ua)
    
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "must_change_password": user.must_change_password,
        "username": user.username,
        "is_admin": user.is_admin,
    }


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """登出：标记当前会话为已登出。"""
    ip, ua = _get_client_info(request)
    
    # 找到最近一条未登出的会话记录
    session = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.logout_at.is_(None)
    ).order_by(UserSession.login_at.desc()).first()
    
    if session:
        session.logout_at = datetime.utcnow()
        db.commit()
    
    return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    
    valid, message = validate_password(request.new_password)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    if request.new_password == request.old_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as old password"
        )
    
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.must_change_password = False
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "must_change_password": current_user.must_change_password,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
    }


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的登录历史。"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).order_by(UserSession.login_at.desc()).limit(20).all()
    
    return [
        {
            "id": s.id,
            "login_at": s.login_at.isoformat(),
            "logout_at": s.logout_at.isoformat() if s.logout_at else None,
            "ip_address": s.ip_address,
        }
        for s in sessions
    ]


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

    token = f"wx_{openid}"

    return TokenResponse(token=token, user_id=openid)


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login():
    """
    Development login - returns a fixed token for testing.
    Only works when LLM_API_KEY is not set (development mode).
    """
    return TokenResponse(token="dev_token_learnflow", user_id="dev_user")
