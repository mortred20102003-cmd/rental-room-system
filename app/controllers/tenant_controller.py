from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.tenant_service import TenantService
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantController:
    def __init__(self, db: Session):
        self.service = TenantService(db)

    def list(self, skip=0, limit=100):
        return self.service.list(skip, limit)

    def get(self, tid: int):
        t = self.service.get(tid)
        if not t:
            raise HTTPException(404, "Tenant not found")
        return t

    def create(self, data: TenantCreate):
        return self.service.create(data)

    def update(self, tid: int, data: TenantUpdate):
        t = self.service.update(tid, data)
        if not t:
            raise HTTPException(404, "Tenant not found")
        return t

    def delete(self, tid: int):
        if not self.service.delete(tid):
            raise HTTPException(404, "Tenant not found")
        return {"message": "Tenant deleted"}
