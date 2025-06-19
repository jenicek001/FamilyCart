from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Shared Shopping List API"
    API_V1_STR: str = "/api/v1"
    # Database
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_DATABASE_URI_ASYNC: Optional[str] = None

    # fastapi-users & JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OAuth Google
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None

    # OAuth Apple
    APPLE_OAUTH_CLIENT_ID: Optional[str] = None # Usually your Bundle ID
    APPLE_OAUTH_TEAM_ID: Optional[str] = None
    APPLE_OAUTH_KEY_ID: Optional[str] = None
    APPLE_OAUTH_PRIVATE_KEY: Optional[str] = None # The content of your .p8 key file

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Add this to ignore extra fields if any

settings = Settings()

# Reason: Construct the database URIs after loading other settings.
if settings.POSTGRES_SERVER and not settings.SQLALCHEMY_DATABASE_URI:
    settings.SQLALCHEMY_DATABASE_URI = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

if settings.POSTGRES_SERVER and not settings.SQLALCHEMY_DATABASE_URI_ASYNC:
    settings.SQLALCHEMY_DATABASE_URI_ASYNC = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
