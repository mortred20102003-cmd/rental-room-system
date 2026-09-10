from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class RoomPhoto(BaseModel):
    room_id: int
    url: str
    caption: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityLog(BaseModel):
    user_id: int
    action: str
    entity: str
    entity_id: Optional[int] = None
    metadata: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TenantMessage(BaseModel):
    lease_id: int
    sender_id: int
    message: str
    attachments: List[str] = []
    sent_at: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsEvent(BaseModel):
    event: str
    data: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)