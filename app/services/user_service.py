from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List

class UserService:
    def __init__(self, db: Session): self.db = db

    def get_by_id(self, uid: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == uid).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create(self, data: UserCreate, is_owner: bool = False) -> User:
        u = User(
            email=data.email, username=data.username,
            hashed_password=data.password, full_name=data.full_name,
            phone=data.phone, is_owner=is_owner,
        )
        self.db.add(u); self.db.commit(); self.db.refresh(u)
        return u

    def update(self, uid: int, data: UserUpdate) -> Optional[User]:
        u = self.get_by_id(uid)
        if not u: return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(u, k, v)
        self.db.commit(); self.db.refresh(u)
        return u

    def delete(self, uid: int) -> bool:
        u = self.get_by_id(uid)
        if not u: return False
        self.db.delete(u); self.db.commit()
        return True