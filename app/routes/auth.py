from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.controllers.auth_controller import AuthController
from app.schemas.user import UserCreate, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    return AuthController(db).register(data)

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return AuthController(db).login(data)