from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentController:
    def __init__(self, db: Session):
        self.service = PaymentService(db)

    def list(self, status=None, lease_id=None, skip=0, limit=100):
        return self.service.list(status, lease_id, skip, limit)

    def overdue(self):
        return self.service.overdue_summary()

    def get(self, pid: int):
        p = self.service.get(pid)
        if not p:
            raise HTTPException(404, "Payment not found")
        return p

    def create(self, data: PaymentCreate):
        return self.service.create(data)

    def update(self, pid: int, data: PaymentUpdate):
        p = self.service.update(pid, data)
        if not p:
            raise HTTPException(404, "Payment not found")
        return p

    def mark_paid(self, pid: int, method: Optional[str] = None):
        p = self.service.mark_paid(pid, method)
        if not p:
            raise HTTPException(404, "Payment not found")
        return p

    def delete(self, pid: int):
        if not self.service.delete(pid):
            raise HTTPException(404, "Payment not found")
        return {"message": "Payment deleted"}
