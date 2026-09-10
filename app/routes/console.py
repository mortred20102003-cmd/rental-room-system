from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_owner
from app.core.config import settings
from app.models.user import User
from app.models.property import Property
from app.models.room import Room
from app.models.tenant import Tenant
from app.models.lease import Lease
from app.models.payment import Payment
from app.models.maintenance import MaintenanceRequest

router = APIRouter(prefix="/console", tags=["Console"])
templates = Jinja2Templates(directory="app/views")


def _base_ctx(request: Request, active: str, current_user: User, **extra):
    ctx = {
        "request": request,
        "active": active,
        "current_user": current_user,
        "app_name": settings.app_name,
        "environment": settings.environment,
    }
    ctx.update(extra)
    return ctx


# ---------- Overview ----------
@router.get("/overview", response_class=HTMLResponse)
def overview(
    request: Request,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    return templates.TemplateResponse(
        "overview.html",
        _base_ctx(request, "overview", owner),
    )


# ---------- Database manager ----------
@router.get("/database", response_class=HTMLResponse)
def database_page(
    request: Request,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    properties = db.query(Property).order_by(Property.id.desc()).all()
    rooms = db.query(Room).order_by(Room.id.desc()).all()
    tenants = db.query(Tenant).order_by(Tenant.id.desc()).all()
    leases = db.query(Lease).order_by(Lease.id.desc()).all()
    payments = db.query(Payment).order_by(Payment.id.desc()).all()

    return templates.TemplateResponse(
        "database.html",
        _base_ctx(
            request,
            "database",
            owner,
            properties=properties,
            rooms=rooms,
            tenants=tenants,
            leases=leases,
            payments=payments,
        ),
    )


# ---------- AI Inspector (placeholder) ----------
@router.get("/ai", response_class=HTMLResponse)
def ai_page(
    request: Request,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    return templates.TemplateResponse(
        "ai_inspector.html",
        _base_ctx(request, "ai", owner),
    )


# ---------- Admin security ----------
@router.get("/security", response_class=HTMLResponse)
def security_page(
    request: Request,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    users = db.query(User).order_by(User.id.desc()).all()
    return templates.TemplateResponse(
        "security.html",
        _base_ctx(request, "security", owner, users=users),
    )


# ---------- Mutations: Properties ----------
@router.post("/database/property/create")
def console_create_property(
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(""),
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    prop = Property(
        name=name.strip(),
        address=address.strip(),
        city=(city.strip() or None),
        owner_id=owner.id,
    )
    db.add(prop)
    db.commit()
    return RedirectResponse("/console/database", status_code=303)


@router.post("/database/property/{pid}/delete")
def console_delete_property(
    pid: int,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    prop = db.query(Property).filter(Property.id == pid).first()
    if prop:
        db.delete(prop)
        db.commit()
    return RedirectResponse("/console/database", status_code=303)


# ---------- Mutations: Rooms ----------
@router.post("/database/room/create")
def console_create_room(
    property_id: int = Form(...),
    room_number: str = Form(...),
    monthly_rent: float = Form(...),
    floor: int = Form(1),
    room_type: str = Form(""),
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(400, f"Property {property_id} does not exist")

    room = Room(
        property_id=property_id,
        room_number=room_number.strip(),
        floor=floor,
        room_type=(room_type.strip() or None),
        monthly_rent=monthly_rent,
    )
    db.add(room)
    db.commit()
    return RedirectResponse("/console/database", status_code=303)


@router.post("/database/room/{rid}/delete")
def console_delete_room(
    rid: int,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    room = db.query(Room).filter(Room.id == rid).first()
    if room:
        db.delete(room)
        db.commit()
    return RedirectResponse("/console/database", status_code=303)


# ---------- Mutations: Tenants ----------
@router.post("/database/tenant/create")
def console_create_tenant(
    full_name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    tenant = Tenant(
        full_name=full_name.strip(),
        email=(email.strip() or None),
        phone=(phone.strip() or None),
    )
    db.add(tenant)
    db.commit()
    return RedirectResponse("/console/database", status_code=303)


@router.post("/database/tenant/{tid}/delete")
def console_delete_tenant(
    tid: int,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    tenant = db.query(Tenant).filter(Tenant.id == tid).first()
    if tenant:
        db.delete(tenant)
        db.commit()
    return RedirectResponse("/console/database", status_code=303)


# ---------- Mutations: Payments ----------
@router.post("/database/payment/{pid}/mark-paid")
def console_mark_paid(
    pid: int,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    from datetime import date
    payment = db.query(Payment).filter(Payment.id == pid).first()
    if payment:
        payment.status = "paid"
        payment.paid_date = date.today()
        db.commit()
    return RedirectResponse("/console/database", status_code=303)


# ---------- Mutations: Users (roles) ----------
@router.post("/security/user/{uid}/toggle-owner")
def console_toggle_owner(
    uid: int,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    if uid == owner.id:
        return RedirectResponse("/console/security?error=self", status_code=303)
    user = db.query(User).filter(User.id == uid).first()
    if user:
        user.is_owner = not user.is_owner
        db.commit()
    return RedirectResponse("/console/security", status_code=303)


@router.post("/security/user/{uid}/toggle-active")
def console_toggle_active(
    uid: int,
    db: Session = Depends(get_db),
    owner: User = Depends(get_current_owner),
):
    if uid == owner.id:
        return RedirectResponse("/console/security?error=self", status_code=303)
    user = db.query(User).filter(User.id == uid).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
    return RedirectResponse("/console/security", status_code=303)