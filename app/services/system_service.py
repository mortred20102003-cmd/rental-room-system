from sqlalchemy.orm import Session
from sqlalchemy import text, func
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import User
from app.models.property import Property
from app.models.room import Room
from app.models.tenant import Tenant
from app.models.lease import Lease
from app.models.payment import Payment
from app.models.maintenance import MaintenanceRequest


class SystemService:
    def __init__(self, db: Session, mongo: AsyncIOMotorDatabase):
        self.db = db
        self.mongo = mongo

    def pg_ok(self) -> bool:
        try:
            self.db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def mongo_ok(self) -> bool:
        try:
            await self.mongo.command("ping")
            return True
        except Exception:
            return False

    async def get_overview(self) -> dict:
        # overdue payments: status != paid AND due_date < today
        overdue = (
            self.db.query(Payment)
            .filter(Payment.status != "paid")
            .filter(Payment.due_date < func.current_date())
            .count()
        )

        return {
            "services": {
                "postgresql": self.pg_ok(),
                "mongodb": await self.mongo_ok(),
            },
            "metrics": {
                "total_properties": self.db.query(Property).count(),
                "total_rooms": self.db.query(Room).count(),
                "occupied_rooms": (
                    self.db.query(Room).filter(Room.is_occupied.is_(True)).count()
                ),
                "vacant_rooms": (
                    self.db.query(Room).filter(Room.is_occupied.is_(False)).count()
                ),
                "total_tenants": self.db.query(Tenant).count(),
                "active_leases": (
                    self.db.query(Lease).filter(Lease.status == "active").count()
                ),
                "pending_payments": (
                    self.db.query(Payment).filter(Payment.status == "pending").count()
                ),
                "overdue_payments": overdue,
                "open_maintenance": (
                    self.db.query(MaintenanceRequest)
                    .filter(MaintenanceRequest.status != "resolved")
                    .count()
                ),
                "users": self.db.query(User).count(),
            },
            "environment": "DEVELOPMENT",
        }