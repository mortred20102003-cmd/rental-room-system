#!/usr/bin/env bash
set -e

# ---------- property_controller.py ----------
cat > app/controllers/property_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.property_service import PropertyService
from app.schemas.property import PropertyCreate, PropertyUpdate


class PropertyController:
    def __init__(self, db: Session):
        self.service = PropertyService(db)

    def list(self, owner_id, skip=0, limit=100):
        return self.service.list(owner_id, skip, limit)

    def get(self, pid: int):
        p = self.service.get(pid)
        if not p:
            raise HTTPException(404, "Property not found")
        return p

    def create(self, data: PropertyCreate, owner_id: int):
        return self.service.create(data, owner_id)

    def update(self, pid: int, data: PropertyUpdate):
        p = self.service.update(pid, data)
        if not p:
            raise HTTPException(404, "Property not found")
        return p

    def delete(self, pid: int):
        if not self.service.delete(pid):
            raise HTTPException(404, "Property not found")
        return {"message": "Property deleted"}
PY

# ---------- room_controller.py ----------
cat > app/controllers/room_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.room_service import RoomService
from app.schemas.room import RoomCreate, RoomUpdate


class RoomController:
    def __init__(self, db: Session):
        self.service = RoomService(db)

    def list(self, property_id=None, occupied=None, skip=0, limit=100):
        return self.service.list(property_id, occupied, skip, limit)

    def get(self, rid: int):
        r = self.service.get(rid)
        if not r:
            raise HTTPException(404, "Room not found")
        return r

    def create(self, data: RoomCreate):
        return self.service.create(data)

    def update(self, rid: int, data: RoomUpdate):
        r = self.service.update(rid, data)
        if not r:
            raise HTTPException(404, "Room not found")
        return r

    def set_occupied(self, rid: int, occupied: bool):
        r = self.service.set_occupied(rid, occupied)
        if not r:
            raise HTTPException(404, "Room not found")
        return r

    def delete(self, rid: int):
        if not self.service.delete(rid):
            raise HTTPException(404, "Room not found")
        return {"message": "Room deleted"}
PY

# ---------- tenant_controller.py ----------
cat > app/controllers/tenant_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.tenant_service import TenantService
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantController:
    def __init__(self, db: Session):
        self.service = TenantService(db)

    def list(self, skip=0, limit=100):
        return self.service.list(skip, limit)

    def get(self, tid: int):
        t = self.service.get(tid)
        if not t:
            raise HTTPException(404, "Tenant not found")
        return t

    def create(self, data: TenantCreate):
        return self.service.create(data)

    def update(self, tid: int, data: TenantUpdate):
        t = self.service.update(tid, data)
        if not t:
            raise HTTPException(404, "Tenant not found")
        return t

    def delete(self, tid: int):
        if not self.service.delete(tid):
            raise HTTPException(404, "Tenant not found")
        return {"message": "Tenant deleted"}
PY

# ---------- lease_controller.py ----------
cat > app/controllers/lease_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.lease_service import LeaseService
from app.schemas.lease import LeaseCreate, LeaseUpdate


class LeaseController:
    def __init__(self, db: Session):
        self.service = LeaseService(db)

    def list(self, status=None, skip=0, limit=100):
        return self.service.list(status, skip, limit)

    def by_tenant(self, tenant_id: int):
        return self.service.list_by_tenant(tenant_id)

    def get(self, lid: int):
        l = self.service.get(lid)
        if not l:
            raise HTTPException(404, "Lease not found")
        return l

    def create(self, data: LeaseCreate):
        return self.service.create(data)

    def update(self, lid: int, data: LeaseUpdate):
        l = self.service.update(lid, data)
        if not l:
            raise HTTPException(404, "Lease not found")
        return l

    def terminate(self, lid: int):
        l = self.service.terminate(lid)
        if not l:
            raise HTTPException(404, "Lease not found")
        return l

    def delete(self, lid: int):
        if not self.service.delete(lid):
            raise HTTPException(404, "Lease not found")
        return {"message": "Lease deleted"}
PY

# ---------- payment_controller.py ----------
cat > app/controllers/payment_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentController:
    def __init__(self, db: Session):
        self.service = PaymentService(db)

    def list(self, status=None, lease_id=None, skip=0, limit=100):
        return self.service.list(status, lease_id, skip, limit)

    def overdue(self):
        return self.service.overdue_summary()

    def get(self, pid: int):
        p = self.service.get(pid)
        if not p:
            raise HTTPException(404, "Payment not found")
        return p

    def create(self, data: PaymentCreate):
        return self.service.create(data)

    def update(self, pid: int, data: PaymentUpdate):
        p = self.service.update(pid, data)
        if not p:
            raise HTTPException(404, "Payment not found")
        return p

    def mark_paid(self, pid: int, method: Optional[str] = None):
        p = self.service.mark_paid(pid, method)
        if not p:
            raise HTTPException(404, "Payment not found")
        return p

    def delete(self, pid: int):
        if not self.service.delete(pid):
            raise HTTPException(404, "Payment not found")
        return {"message": "Payment deleted"}
PY

# ---------- maintenance_controller.py ----------
cat > app/controllers/maintenance_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.maintenance_service import MaintenanceService
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate


class MaintenanceController:
    def __init__(self, db: Session):
        self.service = MaintenanceService(db)

    def list(self, status=None, skip=0, limit=100):
        return self.service.list(status, skip, limit)

    def get(self, mid: int):
        m = self.service.get(mid)
        if not m:
            raise HTTPException(404, "Maintenance request not found")
        return m

    def create(self, data: MaintenanceCreate):
        return self.service.create(data)

    def update(self, mid: int, data: MaintenanceUpdate):
        m = self.service.update(mid, data)
        if not m:
            raise HTTPException(404, "Maintenance request not found")
        return m

    def delete(self, mid: int):
        if not self.service.delete(mid):
            raise HTTPException(404, "Maintenance request not found")
        return {"message": "Maintenance request deleted"}
PY

# ---------- auth_controller.py (idempotent) ----------
cat > app/controllers/auth_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin


class AuthController:
    def __init__(self, db: Session):
        self.service = AuthService(db)

    def register(self, data: UserCreate):
        user, msg = self.service.register(data)
        if not user:
            raise HTTPException(400, msg)
        return {"message": msg, "user_id": user.id}

    def login(self, data: UserLogin):
        result = self.service.login(data)
        if not result:
            raise HTTPException(401, "Incorrect username or password")
        return result
PY

# ---------- system_controller.py (idempotent) ----------
cat > app/controllers/system_controller.py <<'PY'
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.system_service import SystemService


class SystemController:
    def __init__(self, db: Session, mongo: AsyncIOMotorDatabase):
        self.service = SystemService(db, mongo)

    async def overview(self):
        return await self.service.get_overview()
PY

# ---------- user_controller.py (idempotent) ----------
cat > app/controllers/user_controller.py <<'PY'
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.services.user_service import UserService
from app.schemas.user import UserUpdate


class UserController:
    def __init__(self, db: Session):
        self.service = UserService(db)

    def list(self, skip=0, limit=100):
        return self.service.list(skip, limit)

    def get(self, uid: int):
        u = self.service.get_by_id(uid)
        if not u:
            raise HTTPException(404, "User not found")
        return u

    def update(self, uid: int, data: UserUpdate):
        u = self.service.update(uid, data)
        if not u:
            raise HTTPException(404, "User not found")
        return u

    def delete(self, uid: int):
        if not self.service.delete(uid):
            raise HTTPException(404, "User not found")
        return {"message": "User deleted"}
PY

# ---------- ensure __init__.py ----------
touch app/__init__.py app/core/__init__.py app/models/__init__.py \
      app/schemas/__init__.py app/services/__init__.py \
      app/controllers/__init__.py app/routes/__init__.py

echo "✓ All controllers written"
