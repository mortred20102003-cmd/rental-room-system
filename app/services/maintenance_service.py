from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceRequest
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from typing import List, Optional
from datetime import datetime

class MaintenanceService:
    def __init__(self, db: Session): self.db = db

    def get(self, mid: int) -> Optional[MaintenanceRequest]:
        return self.db.query(MaintenanceRequest).filter(MaintenanceRequest.id == mid).first()

    def list(self, status: Optional[str] = None, skip=0, limit=100) -> List[MaintenanceRequest]:
        q = self.db.query(MaintenanceRequest)
        if status: q = q.filter(MaintenanceRequest.status == status)
        return q.offset(skip).limit(limit).all()

    def create(self, data: MaintenanceCreate) -> MaintenanceRequest:
        m = MaintenanceRequest(**data.model_dump())
        self.db.add(m); self.db.commit(); self.db.refresh(m); return m

    def update(self, mid: int, data: MaintenanceUpdate) -> Optional[MaintenanceRequest]:
        m = self.get(mid)
        if not m: return None
        payload = data.model_dump(exclude_unset=True)
        if payload.get("status") == "resolved":
            payload["resolved_at"] = datetime.utcnow()
        for k, v in payload.items(): setattr(m, k, v)
        self.db.commit(); self.db.refresh(m); return m

    def delete(self, mid: int) -> bool:
        m = self.get(mid)
        if not m: return False
        self.db.delete(m); self.db.commit(); return True