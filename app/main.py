from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal, mongodb_client
from app.core.security import get_password_hash
from app.models.user import User
from app.routes import (
    auth, users, properties, rooms, tenants,
    leases, payments, maintenance, system,
)

# create tables
Base.metadata.create_all(bind=engine)

def seed_owner():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == settings.owner_username).first():
            db.add(User(
                email=settings.owner_email,
                username=settings.owner_username,
                hashed_password=get_password_hash(settings.owner_password),
                full_name="Property Owner",
                is_owner=True, is_active=True,
            ))
            db.commit()
            print(f"[seed] owner '{settings.owner_username}' created")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_owner()
    yield
    mongodb_client.close()

app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Public / dashboard
app.include_router(system.router)

# Admin/owner API
for r in (auth, users, properties, rooms, tenants, leases, payments, maintenance):
    app.include_router(r.router, prefix=settings.api_v1_prefix)

@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})