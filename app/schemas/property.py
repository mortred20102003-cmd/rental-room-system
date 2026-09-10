from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PropertyBase(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    description: Optional[str] = None

class PropertyCreate(PropertyBase): pass
class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None

class PropertyResponse(PropertyBase):
    id: int
    owner_id: int
    created_at: datetime
    class Config: from_attributes = True