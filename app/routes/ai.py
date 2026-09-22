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

# ---------- Screen an existing tenant against a room ----------
@router.post("/tenant/{tenant_id}/screen")
async def screen_existing_tenant(
    tenant_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    owner=Depends(get_current_owner),
):
    """
    Body: { "room_id": <int>, "monthly_income": <int>, "employment": "...", "notes": "..." }
    Saves score + verdict back to the tenant record.
    """
    from datetime import datetime, timezone

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")

    room_id = payload.get("room_id")
    if not room_id:
        raise HTTPException(400, "room_id is required in payload")

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(404, f"Room {room_id} not found")

    # Build application dict from tenant + payload
    application = {
        "full_name": tenant.full_name,
        "monthly_income": payload.get("monthly_income", 0),
        "employment": payload.get("employment", "Not specified"),
        "references": payload.get("references", []),
        "notes": payload.get("notes", tenant.emergency_contact or ""),
    }

    room_dict = {
        "room_number": room.room_number,
        "monthly_rent": room.monthly_rent,
        "room_type": room.room_type,
        "deposit_amount": room.deposit_amount,
    }

    result = await gemini_service.screen_tenant(application, room_dict)

    # Persist score back to tenant record
    try:
        score = result.get("score")
        if isinstance(score, (int, float)):
            tenant.screening_score = int(score)
        tenant.screening_verdict = result.get("verdict")
        tenant.screened_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        print(f"[screen] failed to save score to tenant: {e}")

    return result


# ---------- Summarize a lease ----------
@router.post("/lease/{lease_id}/summary")
async def summarize_lease(
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

    # Convert SQLAlchemy objects to plain dicts
    lease_dict = {
        "id": lease.id,
        "start_date": str(lease.start_date),
        "end_date": str(lease.end_date),
        "monthly_rent": lease.monthly_rent,
        "deposit_paid": lease.deposit_paid,
        "status": lease.status,
    }
    tenant_dict = {
        "id": tenant.id,
        "full_name": tenant.full_name,
        "email": tenant.email,
        "phone": tenant.phone,
    }
    room_dict = {
        "id": room.id,
        "room_number": room.room_number,
        "room_type": room.room_type,
        "monthly_rent": room.monthly_rent,
    }

    return await gemini_service.draft_lease_summary(lease_dict, tenant_dict, room_dict)