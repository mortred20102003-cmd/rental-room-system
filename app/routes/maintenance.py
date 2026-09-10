from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.controllers.maintenance_controller import MaintenanceController
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

@router.get("/", response_model=List[MaintenanceResponse])
def list_reqs(status: Optional[str] = None, skip: int = 0, limit: int = 100,
              db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return MaintenanceController(db).list(status, skip, limit)

@router.get("/{mid}", response_model=MaintenanceResponse)
def get_req(mid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return MaintenanceController(db).get(mid)

@router.post("/", response_model=MaintenanceResponse)
def create_req(data: MaintenanceCreate, db: Session = Depends(get_db),
               owner=Depends(get_current_owner)):
    return MaintenanceController(db).create(data)

@router.put("/{mid}", response_model=MaintenanceResponse)
def update_req(mid: int, data: MaintenanceUpdate, db: Session = Depends(get_db),
               owner=Depends(get_current_owner)):
    return MaintenanceController(db).update(mid, data)

@router.patch("/{mid}/resolve", response_model=MaintenanceResponse)
def resolve_req(mid: int, db: Session = Depends(get_db),
                owner=Depends(get_current_owner)):
    return MaintenanceController(db).update(mid, MaintenanceUpdate(status="resolved"))

@router.delete("/{mid}")
def delete_req(mid: int, db: Session = Depends(get_db),
               owner=Depends(get_current_owner)):
    return MaintenanceController(db).delete(mid)