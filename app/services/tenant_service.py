from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate
from typing import List, Optional

class TenantService:
    def __init__(self, db: Session): self.db = db

    def get(self, tid: int) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.id == tid).first()

    def list(self, skip=0, limit=100) -> List[Tenant]:
        return self.db.query(Tenant).offset(skip).limit(limit).all()

    def create(self, data: TenantCreate) -> Tenant:
        t = Tenant(**data.model_dump())
        self.db.add(t); self.db.commit(); self.db.refresh(t); return t

    def update(self, tid: int, data: TenantUpdate) -> Optional[Tenant]:
        t = self.get(tid)
        if not t: return None
        for k, v in data.model_dump(exclude_unset=True).items(): setattr(t, k, v)
        self.db.commit(); self.db.refresh(t); return t

    def delete(self, tid: int) -> bool:
        t = self.get(tid)
        if not t: return False
        self.db.delete(t); self.db.commit(); return True