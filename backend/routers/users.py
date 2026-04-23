from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.core.config import settings
from backend.models.user import User
from backend.schemas.user import UserResponse

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "phone_number": current_user.phone_number,
        "full_name": current_user.full_name,
        "username": current_user.username,
        "language": current_user.language,
        "unique_code": current_user.unique_code,
        "dashboard_url": f"{settings.FRONTEND_URL}/dashboard/{current_user.unique_code}",
    }
