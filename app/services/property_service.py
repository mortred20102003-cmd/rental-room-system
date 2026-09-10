from sqlalchemy.orm import Session
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate
from typing import List, Optional

class PropertyService:
    def __init__(self, db: Session): self.db = db

    def get(self, pid: int) -> Optional[Property]:
        return self.db.query(Property).filter(Property.id == pid).first()

    def list(self, owner_id: Optional[int] = None, skip=0, limit=100) -> List[Property]:
        q = self.db.query(Property)
        if owner_id: q = q.filter(Property.owner_id == owner_id)
        return q.offset(skip).limit(limit).all()

    def create(self, data: PropertyCreate, owner_id: int) -> Property:
        p = Property(**data.model_dump(), owner_id=owner_id)
        self.db.add(p); self.db.commit(); self.db.refresh(p)
        return p

    def update(self, pid: int, data: PropertyUpdate) -> Optional[Property]:
        p = self.get(pid)
        if not p: return None
        for k, v in data.model_dump(exclude_unset=True).items(): setattr(p, k, v)
        self.db.commit(); self.db.refresh(p)
        return p

    def delete(self, pid: int) -> bool:
        p = self.get(pid)
        if not p: return False
        self.db.delete(p); self.db.commit(); return True