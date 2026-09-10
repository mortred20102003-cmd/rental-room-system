from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin


class AuthController:
    def __init__(self, db: Session):
        self.service = AuthService(db)

    def register(self, data: UserCreate):
        user, msg = self.service.register(data)
        if not user:
            raise HTTPException(400, msg)
        return {"message": msg, "user_id": user.id}

    def login(self, data: UserLogin):
        result = self.service.login(data)
        if not result:
            raise HTTPException(401, "Incorrect username or password")
        return result
