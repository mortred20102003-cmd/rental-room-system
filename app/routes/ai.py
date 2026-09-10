from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db, mongodb_db
from app.core.dependencies import get_current_owner
from app.models.room import Room
from app.models.lease import Lease
from app.models.tenant import Tenant
from app.services import gemini_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


# ---------- Tenant screening ----------
@router.post("/tenant/screen")
async def screen_tenant(
    payload: dict,
    room_id: int,
    db: Session = Depends(get_db),
    owner=Depends(get_current_owner),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, "Room not found")

    room_dict = {
        "room_number": room.room_number,
        "monthly_rent": room.monthly_rent,
        "room_type": room.room_type,
        "deposit_amount": room.deposit_amount,
    }
    return await gemini_service.screen_tenant(payload, room_dict)


# ---------- Maintenance triage ----------
@router.post("/maintenance/classify")
async def classify_maintenance(
    payload: dict,
    owner=Depends(get_current_owner),
):
    if not payload.get("title"):
        raise HTTPException(400, "title is required")
    return await gemini_service.classify_maintenance(
        payload["title"], payload.get("description", "")
    )


# ---------- Lease summary ----------
@router.post("/lease/{lease_id}/summary")
async def lease_summary(
    lease_id: int,
    db: Session = Depends(get_db),
    owner=Depends(get_current_owner),
):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(404, "Lease not found")

    tenant = db.query(Tenant).filter(Tenant.id == lease.tenant_id).first()
    room = db.query(Room).filter(Room.id == lease.room_id).first()
    if not tenant or not room:
        raise HTTPException(400, "Lease references missing tenant or room")

    return await gemini_service.draft_lease_summary(
        lease.__dict__, tenant.__dict__, room.__dict__
    )


# ---------- AI log inspector ----------
@router.get("/logs")
async def list_logs(
    kind: str | None = None,
    limit: int = 50,
    owner=Depends(get_current_owner),
):
    query = {"kind": kind} if kind else {}
    cursor = mongodb_db["ai_logs"].find(query).sort("timestamp", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    for d in docs:
        d["_id"] = str(d["_id"])
        if isinstance(d.get("timestamp"), object):
            d["timestamp"] = str(d["timestamp"])
    return docs