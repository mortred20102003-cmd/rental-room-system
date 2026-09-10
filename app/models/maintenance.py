from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, default="normal")      # low / normal / high / urgent
    status = Column(String, default="open")          # open / in_progress / resolved
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)