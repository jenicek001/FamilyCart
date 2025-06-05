from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shared Shopping List API"
    API_V1_STR: str = "/api/v1"
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str | None = None # Assembled from above

    # fastapi-users & JWT
    SECRET_KEY: str # For JWT signing
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OAuth Google
    GOOGLE_OAUTH_CLIENT_ID: str | None = None
    GOOGLE_OAUTH_CLIENT_SECRET: str | None = None

    # OAuth Apple
    APPLE_OAUTH_CLIENT_ID: str | None = None # Usually your Bundle ID
    APPLE_OAUTH_TEAM_ID: str | None = None
    APPLE_OAUTH_KEY_ID: str | None = None
    APPLE_OAUTH_PRIVATE_KEY: str | None = None # The content of your .p8 key file

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

if not settings.DATABASE_URL and settings.POSTGRES_SERVER:
    settings.DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
