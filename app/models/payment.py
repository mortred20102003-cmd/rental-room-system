from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    lease_id = Column(Integer, ForeignKey("leases.id"))
    amount = Column(Float, nullable=False)
    due_date = Column(Date)
    paid_date = Column(Date, nullable=True)
    status = Column(String, default="pending")       # pending / paid / overdue
    method = Column(String)                          # cash / bank / ewallet
    reference = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())