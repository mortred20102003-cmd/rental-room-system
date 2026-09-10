from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoomBase(BaseModel):
    property_id: int
    room_number: str
    floor: int = 1
    room_type: Optional[str] = None
    monthly_rent: float
    deposit_amount: float = 0
    area_sqm: Optional[float] = None
    notes: Optional[str] = None

class RoomCreate(RoomBase): pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    floor: Optional[int] = None
    room_type: Optional[str] = None
    monthly_rent: Optional[float] = None
    deposit_amount: Optional[float] = None
    area_sqm: Optional[float] = None
    is_occupied: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class RoomResponse(RoomBase):
    id: int
    is_occupied: bool
    is_active: bool
    created_at: datetime
    class Config: from_attributes = True