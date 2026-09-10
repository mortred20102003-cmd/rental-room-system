from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_owner
from app.controllers.user_controller import UserController
from app.schemas.user import UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return UserController(db).list(skip, limit)

@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)): return user

@router.get("/{uid}", response_model=UserResponse)
def get_user(uid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return UserController(db).get(uid)

@router.put("/{uid}", response_model=UserResponse)
def update_user(uid: int, data: UserUpdate, db: Session = Depends(get_db),
                owner=Depends(get_current_owner)):
    return UserController(db).update(uid, data)

@router.delete("/{uid}")
def delete_user(uid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return UserController(db).delete(uid)