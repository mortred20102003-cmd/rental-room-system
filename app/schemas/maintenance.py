from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaintenanceBase(BaseModel):
    room_id: int
    tenant_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: str = "normal"

class MaintenanceCreate(MaintenanceBase): pass

class MaintenanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class MaintenanceResponse(MaintenanceBase):
    id: int
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    class Config: from_attributes = True