from sqlalchemy.orm import Session
from app.models.lease import Lease
from app.schemas.lease import LeaseCreate, LeaseUpdate
from typing import List, Optional
from datetime import date
from fastapi import HTTPException
from app.models.room import Room
from app.models.tenant import Tenant


class LeaseService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, lid: int) -> Optional[Lease]:
        return self.db.query(Lease).filter(Lease.id == lid).first()

    def list(self, status: Optional[str] = None, skip=0, limit=100) -> List[Lease]:
        q = self.db.query(Lease)
        if status:
            q = q.filter(Lease.status == status)
        return q.offset(skip).limit(limit).all()

    def list_by_tenant(self, tenant_id: int) -> List[Lease]:
        return self.db.query(Lease).filter(Lease.tenant_id == tenant_id).all()

    def create(self, data: LeaseCreate) -> Lease:
        # Validate room exists
        room = self.db.query(Room).filter(Room.id == data.room_id).first()
        if not room:
            raise HTTPException(400, f"Room {data.room_id} does not exist")

        # Validate tenant exists
        tenant = self.db.query(Tenant).filter(Tenant.id == data.tenant_id).first()
        if not tenant:
            raise HTTPException(400, f"Tenant {data.tenant_id} does not exist")

        # Validate dates
        if data.end_date <= data.start_date:
            raise HTTPException(400, "end_date must be after start_date")

        # Create lease and auto-mark room occupied
        l = Lease(**data.model_dump(), status="active")
        room.is_occupied = True
        self.db.add(l)
        self.db.commit()
        self.db.refresh(l)
        return l

    def update(self, lid: int, data: LeaseUpdate) -> Optional[Lease]:
        l = self.get(lid)
        if not l:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(l, k, v)
        self.db.commit()
        self.db.refresh(l)
        return l

    def terminate(self, lid: int) -> Optional[Lease]:
        l = self.get(lid)
        if not l:
            return None

        l.status = "ended"
        l.end_date = date.today()

        # Free the room when the lease ends
        room = self.db.query(Room).filter(Room.id == l.room_id).first()
        if room:
            room.is_occupied = False

        self.db.commit()
        self.db.refresh(l)
        return l

    def delete(self, lid: int) -> bool:
        l = self.get(lid)
        if not l:
            return False
        self.db.delete(l)
        self.db.commit()
        return True