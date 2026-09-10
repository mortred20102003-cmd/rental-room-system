from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.controllers.lease_controller import LeaseController
from app.schemas.lease import LeaseCreate, LeaseUpdate, LeaseResponse

router = APIRouter(prefix="/leases", tags=["Leases"])

@router.get("/", response_model=List[LeaseResponse])
def list_leases(status: Optional[str] = None, skip: int = 0, limit: int = 100,
                db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return LeaseController(db).list(status, skip, limit)

@router.get("/{lid}", response_model=LeaseResponse)
def get_lease(lid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return LeaseController(db).get(lid)

@router.get("/tenant/{tid}", response_model=List[LeaseResponse])
def leases_by_tenant(tid: int, db: Session = Depends(get_db),
                     owner=Depends(get_current_owner)):
    return LeaseController(db).by_tenant(tid)

@router.post("/", response_model=LeaseResponse)
def create_lease(data: LeaseCreate, db: Session = Depends(get_db),
                 owner=Depends(get_current_owner)):
    return LeaseController(db).create(data)

@router.put("/{lid}", response_model=LeaseResponse)
def update_lease(lid: int, data: LeaseUpdate, db: Session = Depends(get_db),
                 owner=Depends(get_current_owner)):
    return LeaseController(db).update(lid, data)

@router.patch("/{lid}/terminate", response_model=LeaseResponse)
def terminate_lease(lid: int, db: Session = Depends(get_db),
                    owner=Depends(get_current_owner)):
    return LeaseController(db).terminate(lid)

@router.delete("/{lid}")
def delete_lease(lid: int, db: Session = Depends(get_db),
                 owner=Depends(get_current_owner)):
    return LeaseController(db).delete(lid)