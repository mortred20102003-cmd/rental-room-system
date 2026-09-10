from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.room_service import RoomService
from app.schemas.room import RoomCreate, RoomUpdate


class RoomController:
    def __init__(self, db: Session):
        self.service = RoomService(db)

    def list(self, property_id=None, occupied=None, skip=0, limit=100):
        return self.service.list(property_id, occupied, skip, limit)

    def get(self, rid: int):
        r = self.service.get(rid)
        if not r:
            raise HTTPException(404, "Room not found")
        return r

    def create(self, data: RoomCreate):
        return self.service.create(data)

    def update(self, rid: int, data: RoomUpdate):
        r = self.service.update(rid, data)
        if not r:
            raise HTTPException(404, "Room not found")
        return r

    def set_occupied(self, rid: int, occupied: bool):
        r = self.service.set_occupied(rid, occupied)
        if not r:
            raise HTTPException(404, "Room not found")
        return r

    def delete(self, rid: int):
        if not self.service.delete(rid):
            raise HTTPException(404, "Room not found")
        return {"message": "Room deleted"}
