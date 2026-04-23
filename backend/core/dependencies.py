from fastapi import Header, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db  # re-exported for convenience
from backend.models.user import User
from backend.core.config import settings
from fastapi import Depends


async def get_current_user(
    x_user_code: str = Header(..., alias="X-User-Code"),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.unique_code == x_user_code).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing user code",
        )
    return user


async def verify_internal_key(
    x_internal_key: str = Header(..., alias="X-Internal-Key"),
) -> None:
    if x_internal_key != settings.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid internal key")
