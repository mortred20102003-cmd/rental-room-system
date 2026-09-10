from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class TenantBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    emergency_contact: Optional[str] = None

class TenantCreate(TenantBase): pass

class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    is_active: Optional[bool] = None

class TenantResponse(TenantBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config: from_attributes = True