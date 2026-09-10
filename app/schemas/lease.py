from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class LeaseBase(BaseModel):
    room_id: int
    tenant_id: int
    start_date: date
    end_date: date
    monthly_rent: float
    deposit_paid: float = 0

class LeaseCreate(LeaseBase): pass

class LeaseUpdate(BaseModel):
    end_date: Optional[date] = None
    monthly_rent: Optional[float] = None
    deposit_paid: Optional[float] = None
    status: Optional[str] = None

class LeaseResponse(LeaseBase):
    id: int
    status: str
    created_at: datetime
    class Config: from_attributes = True