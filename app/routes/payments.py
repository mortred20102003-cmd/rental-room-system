from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.controllers.payment_controller import PaymentController
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=List[PaymentResponse])
def list_payments(status: Optional[str] = None, lease_id: Optional[int] = None,
                  skip: int = 0, limit: int = 100,
                  db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return PaymentController(db).list(status, lease_id, skip, limit)

@router.get("/overdue", response_model=List[PaymentResponse])
def overdue(db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return PaymentController(db).overdue()

@router.get("/{pid}", response_model=PaymentResponse)
def get_payment(pid: int, db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return PaymentController(db).get(pid)

@router.post("/", response_model=PaymentResponse)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db),
                   owner=Depends(get_current_owner)):
    return PaymentController(db).create(data)

@router.put("/{pid}", response_model=PaymentResponse)
def update_payment(pid: int, data: PaymentUpdate, db: Session = Depends(get_db),
                   owner=Depends(get_current_owner)):
    return PaymentController(db).update(pid, data)

@router.patch("/{pid}/mark-paid", response_model=PaymentResponse)
def mark_paid(pid: int, method: Optional[str] = None,
              db: Session = Depends(get_db), owner=Depends(get_current_owner)):
    return PaymentController(db).mark_paid(pid, method)

@router.delete("/{pid}")
def delete_payment(pid: int, db: Session = Depends(get_db),
                   owner=Depends(get_current_owner)):
    return PaymentController(db).delete(pid)