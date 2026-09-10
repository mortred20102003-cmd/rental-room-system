from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rooms = relationship("Room", back_populates="property", cascade="all, delete-orphan")