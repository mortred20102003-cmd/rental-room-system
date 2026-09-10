from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.property_service import PropertyService
from app.schemas.property import PropertyCreate, PropertyUpdate


class PropertyController:
    def __init__(self, db: Session):
        self.service = PropertyService(db)

    def list(self, owner_id, skip=0, limit=100):
        return self.service.list(owner_id, skip, limit)

    def get(self, pid: int):
        p = self.service.get(pid)
        if not p:
            raise HTTPException(404, "Property not found")
        return p

    def create(self, data: PropertyCreate, owner_id: int):
        return self.service.create(data, owner_id)

    def update(self, pid: int, data: PropertyUpdate):
        p = self.service.update(pid, data)
        if not p:
            raise HTTPException(404, "Property not found")
        return p

    def delete(self, pid: int):
        if not self.service.delete(pid):
            raise HTTPException(404, "Property not found")
        return {"message": "Property deleted"}
