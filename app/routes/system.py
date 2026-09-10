from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_db, get_mongodb
from app.controllers.system_controller import SystemController

router = APIRouter(tags=["System"])

@router.get("/system/overview")
async def overview(db: Session = Depends(get_db),
                   mongo: AsyncIOMotorDatabase = Depends(get_mongodb)):
    return await SystemController(db, mongo).overview()

@router.get("/system/health")
async def health(db: Session = Depends(get_db),
                 mongo: AsyncIOMotorDatabase = Depends(get_mongodb)):
    c = SystemController(db, mongo)
    return {"postgresql": c.service.pg_ok(), "mongodb": await c.service.mongo_ok()}