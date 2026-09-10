from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_user(token: str, db: Session):
    payload = decode_access_token(token)
    if not payload:
        return None
    return UserService(db).get_by_id(payload.get("user_id"))


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    # 1. Bearer header (API clients, Swagger)
    if credentials and credentials.credentials:
        user = _resolve_user(credentials.credentials, db)
        if user:
            return user

    # 2. HttpOnly cookie (HTML console)
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        user = _resolve_user(cookie_token, db)
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_owner(user=Depends(get_current_user)):
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner/Admin privileges required")
    return user
