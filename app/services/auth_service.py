from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.user import UserCreate, UserLogin

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserService(db)

    def register(self, data: UserCreate):
        if self.users.get_by_email(data.email):
            return None, "Email already registered"
        if self.users.get_by_username(data.username):
            return None, "Username taken"
        data.password = get_password_hash(data.password)
        return self.users.create(data), "User created"

    def login(self, data: UserLogin):
        user = self.users.get_by_username(data.username)
        if not user or not verify_password(data.password, user.hashed_password):
            return None
        token = create_access_token({"user_id": user.id, "username": user.username})
        return {"access_token": token, "token_type": "bearer"}