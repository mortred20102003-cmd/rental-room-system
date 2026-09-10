from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.user_service import UserService
from app.schemas.user import UserUpdate


class UserController:
    def __init__(self, db: Session):
        self.service = UserService(db)

    def list(self, skip=0, limit=100):
        return self.service.list(skip, limit)

    def get(self, uid: int):
        u = self.service.get_by_id(uid)
        if not u:
            raise HTTPException(404, "User not found")
        return u

    def update(self, uid: int, data: UserUpdate):
        u = self.service.update(uid, data)
        if not u:
            raise HTTPException(404, "User not found")
        return u

    def delete(self, uid: int):
        if not self.service.delete(uid):
            raise HTTPException(404, "User not found")
        return {"message": "User deleted"}
