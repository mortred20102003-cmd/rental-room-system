from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.lease_service import LeaseService
from app.schemas.lease import LeaseCreate, LeaseUpdate


class LeaseController:
    def __init__(self, db: Session):
        self.service = LeaseService(db)

    def list(self, status=None, skip=0, limit=100):
        return self.service.list(status, skip, limit)

    def by_tenant(self, tenant_id: int):
        return self.service.list_by_tenant(tenant_id)

    def get(self, lid: int):
        l = self.service.get(lid)
        if not l:
            raise HTTPException(404, "Lease not found")
        return l

    def create(self, data: LeaseCreate):
        return self.service.create(data)

    def update(self, lid: int, data: LeaseUpdate):
        l = self.service.update(lid, data)
        if not l:
            raise HTTPException(404, "Lease not found")
        return l

    def terminate(self, lid: int):
        l = self.service.terminate(lid)
        if not l:
            raise HTTPException(404, "Lease not found")
        return l

    def delete(self, lid: int):
        if not self.service.delete(lid):
            raise HTTPException(404, "Lease not found")
        return {"message": "Lease deleted"}
