from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

engine = create_engine(settings.postgresql_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
mongodb_db = mongodb_client[settings.mongodb_db_name]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_mongodb():
    return mongodb_db