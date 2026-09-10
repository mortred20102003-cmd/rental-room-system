from sqlalchemy.orm import Session
from app.models.lease import Lease
from app.schemas.lease import LeaseCreate, LeaseUpdate
from typing import List, Optional
from datetime import date

class LeaseService:
    def __init__(self, db: Session): self.db = db

    def get(self, lid: int) -> Optional[Lease]:
        return self.db.query(Lease).filter(Lease.id == lid).first()

    def list(self, status: Optional[str] = None, skip=0, limit=100) -> List[Lease]:
        q = self.db.query(Lease)
        if status: q = q.filter(Lease.status == status)
        return q.offset(skip).limit(limit).all()

    def list_by_tenant(self, tenant_id: int) -> List[Lease]:
        return self.db.query(Lease).filter(Lease.tenant_id == tenant_id).all()

    def create(self, data: LeaseCreate) -> Lease:
        l = Lease(**data.model_dump(), status="active")
        self.db.add(l); self.db.commit(); self.db.refresh(l); return l

    def update(self, lid: int, data: LeaseUpdate) -> Optional[Lease]:
        l = self.get(lid)
        if not l: return None
        for k, v in data.model_dump(exclude_unset=True).items(): setattr(l, k, v)
        self.db.commit(); self.db.refresh(l); return l

    def terminate(self, lid: int) -> Optional[Lease]:
        return self.update(lid, LeaseUpdate(status="ended", end_date=date.today()))

    def delete(self, lid: int) -> bool:
        l = self.get(lid)
        if not l: return False
        self.db.delete(l); self.db.commit(); return True