from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    room_number = Column(String, nullable=False, index=True)
    floor = Column(Integer, default=1)
    room_type = Column(String)                       # single / double / studio
    monthly_rent = Column(Float, nullable=False)
    deposit_amount = Column(Float, default=0)
    area_sqm = Column(Float)
    is_occupied = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="rooms")