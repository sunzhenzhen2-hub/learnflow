"""Profile router - 个人学习统计。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..dependencies import get_current_user_or_none

router = APIRouter()


@router.get("/")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_none),
):
    """获取个人学习统计数据（按用户隔离）。"""
    user = current_user
    if not user:
        # Get or create guest user
        guest = db.query(User).filter(User.username == "guest").first()
        if not guest:
            from ..services.auth import get_password_hash
            guest = User(
                username="guest",
                hashed_password=get_password_hash("guest"),
                is_active=True,
                is_admin=False,
            )
            db.add(guest)
            db.flush()
        user = guest
    from ..services.profile import get_profile_data
    return get_profile_data(user.id)
