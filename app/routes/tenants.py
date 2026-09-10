from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.controllers.tenant_controller import TenantController
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/", response_model=List[TenantResponse])
def list_tenants(skip: int = 0, limit: int = 100,
                 db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return TenantController(db).list(skip, limit)

@router.get("/{tid}", response_model=TenantResponse)
def get_tenant(tid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return TenantController(db).get(tid)

@router.post("/", response_model=TenantResponse)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db),
                  owner=Depends(get_current_owner)):
    return TenantController(db).create(data)

@router.put("/{tid}", response_model=TenantResponse)
def update_tenant(tid: int, data: TenantUpdate, db: Session = Depends(get_db),
                  owner=Depends(get_current_owner)):
    return TenantController(db).update(tid, data)

@router.delete("/{tid}")
def delete_tenant(tid: int, db: Session = Depends(get_db),
                  owner=Depends(get_current_owner)):
    return TenantController(db).delete(tid)