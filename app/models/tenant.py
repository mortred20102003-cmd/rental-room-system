from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    id_number = Column(String)
    emergency_contact = Column(String)
    is_active = Column(Boolean, default=True)

    # AI screening results
    screening_score = Column(Integer, nullable=True)
    screening_verdict = Column(String, nullable=True)
    screened_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())