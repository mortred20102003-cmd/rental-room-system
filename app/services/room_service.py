from sqlalchemy.orm import Session
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate
from typing import List, Optional

class RoomService:
    def __init__(self, db: Session): self.db = db

    def get(self, rid: int) -> Optional[Room]:
        return self.db.query(Room).filter(Room.id == rid).first()

    def list(self, property_id: Optional[int] = None,
             occupied: Optional[bool] = None,
             skip=0, limit=100) -> List[Room]:
        q = self.db.query(Room)
        if property_id: q = q.filter(Room.property_id == property_id)
        if occupied is not None: q = q.filter(Room.is_occupied == occupied)
        return q.offset(skip).limit(limit).all()

    def create(self, data: RoomCreate) -> Room:
        r = Room(**data.model_dump())
        self.db.add(r); self.db.commit(); self.db.refresh(r); return r

    def update(self, rid: int, data: RoomUpdate) -> Optional[Room]:
        r = self.get(rid)
        if not r: return None
        for k, v in data.model_dump(exclude_unset=True).items(): setattr(r, k, v)
        self.db.commit(); self.db.refresh(r); return r

    def delete(self, rid: int) -> bool:
        r = self.get(rid)
        if not r: return False
        self.db.delete(r); self.db.commit(); return True

    def set_occupied(self, rid: int, occupied: bool) -> Optional[Room]:
        return self.update(rid, RoomUpdate(is_occupied=occupied))