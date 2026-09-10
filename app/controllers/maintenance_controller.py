from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.maintenance_service import MaintenanceService
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate


class MaintenanceController:
    def __init__(self, db: Session):
        self.service = MaintenanceService(db)

    def list(self, status=None, skip=0, limit=100):
        return self.service.list(status, skip, limit)

    def get(self, mid: int):
        m = self.service.get(mid)
        if not m:
            raise HTTPException(404, "Maintenance request not found")
        return m

    def create(self, data: MaintenanceCreate):
        return self.service.create(data)

    def update(self, mid: int, data: MaintenanceUpdate):
        m = self.service.update(mid, data)
        if not m:
            raise HTTPException(404, "Maintenance request not found")
        return m

    def delete(self, mid: int):
        if not self.service.delete(mid):
            raise HTTPException(404, "Maintenance request not found")
        return {"message": "Maintenance request deleted"}
