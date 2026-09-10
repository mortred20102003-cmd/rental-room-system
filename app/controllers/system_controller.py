from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.system_service import SystemService


class SystemController:
    def __init__(self, db: Session, mongo: AsyncIOMotorDatabase):
        self.service = SystemService(db, mongo)

    async def overview(self):
        return await self.service.get_overview()
