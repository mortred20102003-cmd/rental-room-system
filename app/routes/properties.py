from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.controllers.property_controller import PropertyController
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.get("/", response_model=List[PropertyResponse])
def list_properties(skip: int = 0, limit: int = 100,
                    db: Session = Depends(get_db),
                    owner=Depends(get_current_owner)):
    return PropertyController(db).list(owner.id, skip, limit)

@router.get("/{pid}", response_model=PropertyResponse)
def get_property(pid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return PropertyController(db).get(pid)

@router.post("/", response_model=PropertyResponse)
def create_property(data: PropertyCreate, db: Session = Depends(get_db),
                    owner=Depends(get_current_owner)):
    return PropertyController(db).create(data, owner.id)

@router.put("/{pid}", response_model=PropertyResponse)
def update_property(pid: int, data: PropertyUpdate, db: Session = Depends(get_db),
                    owner=Depends(get_current_owner)):
    return PropertyController(db).update(pid, data)

@router.delete("/{pid}")
def delete_property(pid: int, db: Session = Depends(get_db),
                    owner=Depends(get_current_owner)):
    return PropertyController(db).delete(pid)