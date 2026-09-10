from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    postgresql_url: str
    mongodb_url: str
    mongodb_db_name: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    owner_email: str
    owner_username: str
    owner_password: str

    app_name: str
    api_v1_prefix: str
    debug: bool
    environment: str
    backend_cors_origins: List[str]

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore", 
    )

settings = Settings()