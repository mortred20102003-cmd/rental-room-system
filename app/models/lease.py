from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Lease(Base):
    __tablename__ = "leases"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    deposit_paid = Column(Float, default=0)
    status = Column(String, default="active")        # active / ended / cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room")
    tenant = relationship("Tenant")