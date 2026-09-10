import json
from typing import List, Optional
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL
    postgresql_url: str
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None

    # MongoDB
    mongodb_url: str
    mongodb_db_name: str = "rental_mongo"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Owner / Admin (superAdmin seed)
    owner_email: str
    owner_username: str
    owner_password: str

    # Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # App
    app_name: str = "Rental Room Management System"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    environment: str = "PRODUCTION"
    backend_cors_origins: List[str] = ["http://localhost:8000"]

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()