"""Profile router - 个人学习统计。"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_profile():
    """获取个人学习统计数据。"""
    from ..services.profile import get_profile_data
    return get_profile_data()
