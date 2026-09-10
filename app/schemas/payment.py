from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class PaymentBase(BaseModel):
    lease_id: int
    amount: float
    due_date: Optional[date] = None
    method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase): pass

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    status: Optional[str] = None
    method: Optional[str] = None
    reference: Optional[str] = None
    notes: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    paid_date: Optional[date] = None
    status: str
    created_at: datetime
    class Config: from_attributes = True