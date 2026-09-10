from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.user_service import UserService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    user = UserService(db).get_by_id(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_owner(user=Depends(get_current_user)):
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner/Admin privileges required")
    return user