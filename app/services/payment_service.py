from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.payment import Payment
from app.models.lease import Lease
from app.schemas.payment import PaymentCreate, PaymentUpdate
from typing import List, Optional
from datetime import date

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, pid: int) -> Optional[Payment]:
        return self.db.query(Payment).filter(Payment.id == pid).first()

    def list(self, status=None, lease_id=None, skip=0, limit=100) -> List[Payment]:
        q = self.db.query(Payment)
        if status: q = q.filter(Payment.status == status)
        if lease_id: q = q.filter(Payment.lease_id == lease_id)
        return q.offset(skip).limit(limit).all()

    def create(self, data: PaymentCreate) -> Payment:
        # Validate lease exists
        lease = self.db.query(Lease).filter(Lease.id == data.lease_id).first()
        if not lease:
            raise HTTPException(
                status_code=400,
                detail=f"Lease {data.lease_id} does not exist. Create the lease first."
            )

        if data.amount <= 0:
            raise HTTPException(400, "amount must be greater than 0")

        p = Payment(**data.model_dump(), status="pending")
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def update(self, pid: int, data: PaymentUpdate) -> Optional[Payment]:
        p = self.get(pid)
        if not p: return None
        for k, v in data.model_dump(exclude_unset=True).items(): setattr(p, k, v)
        self.db.commit(); self.db.refresh(p); return p

    def mark_paid(self, pid: int, method: Optional[str] = None) -> Optional[Payment]:
        return self.update(pid, PaymentUpdate(
            status="paid", paid_date=date.today(), method=method
        ))

    def delete(self, pid: int) -> bool:
        p = self.get(pid)
        if not p: return False
        self.db.delete(p); self.db.commit(); return True

    def overdue_summary(self) -> List[Payment]:
        return self.db.query(Payment).filter(Payment.status != "paid",
                                             Payment.due_date < date.today()).all()