from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal, mongodb_client, get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User

# ---------- API routers ----------
from app.routes import (
    auth, users, properties, rooms, tenants,
    leases, payments, maintenance, system, ai,
)
# ---------- Console router ----------
from app.routes import console


# ---------- Create tables on import ----------
Base.metadata.create_all(bind=engine)


# ---------- Seed superAdmin owner ----------
def seed_owner():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == settings.owner_username).first():
            db.add(User(
                email=settings.owner_email,
                username=settings.owner_username,
                hashed_password=get_password_hash(settings.owner_password),
                full_name="Property Owner",
                is_owner=True,
                is_active=True,
            ))
            db.commit()
            print(f"[seed] owner '{settings.owner_username}' created")
    finally:
        db.close()


# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_owner()
    yield
    mongodb_client.close()


# ---------- App ----------
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Static + Templates ----------
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")   # used for / and /login
console_templates = Jinja2Templates(directory="app/views")  # used by console router


# ---------- API routers ----------
app.include_router(system.router)                                        # /system/*
app.include_router(auth.router,        prefix=settings.api_v1_prefix)    # /api/v1/auth/*
app.include_router(users.router,       prefix=settings.api_v1_prefix)    # /api/v1/users/*
app.include_router(properties.router,  prefix=settings.api_v1_prefix)    # /api/v1/properties/*
app.include_router(rooms.router,       prefix=settings.api_v1_prefix)    # /api/v1/rooms/*
app.include_router(tenants.router,     prefix=settings.api_v1_prefix)    # /api/v1/tenants/*
app.include_router(leases.router,      prefix=settings.api_v1_prefix)    # /api/v1/leases/*
app.include_router(payments.router,    prefix=settings.api_v1_prefix)    # /api/v1/payments/*
app.include_router(maintenance.router, prefix=settings.api_v1_prefix)    # /api/v1/maintenance/*
app.include_router(ai.router)                                            # /api/v1/ai/*

# ---------- Console ----------
app.include_router(console.router)                                       # /console/*


# ---------- Public dashboard ----------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "app_name": settings.app_name,
        "environment": settings.environment,
    })


# ---------- HTML login (cookie auth) ----------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "app_name": settings.app_name,
        "environment": settings.environment,
    })


@app.post("/login")
def login_submit(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse("/login?error=1", status_code=303)

    token = create_access_token({"user_id": user.id, "username": user.username})
    redirect = RedirectResponse("/console/overview", status_code=303)
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.environment == "PRODUCTION",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return redirect


@app.get("/logout")
def logout():
    redirect = RedirectResponse("/login", status_code=303)
    redirect.delete_cookie("access_token")
    return redirect