from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Shared Shopping List API"
    API_V1_STR: str = "/api/v1"

    # Server Configuration
    PORT: int = 8005
    HOST: str = "0.0.0.0"

    # Database
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_DATABASE_URI_ASYNC: Optional[str] = None

    @model_validator(mode="after")
    def get_db_connection_str(self) -> "Settings":
        if (
            self.POSTGRES_USER
            and self.POSTGRES_PASSWORD
            and self.POSTGRES_SERVER
            and self.POSTGRES_DB
        ):
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
            self.SQLALCHEMY_DATABASE_URI_ASYNC = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    # fastapi-users & JWT
    SECRET_KEY: str = "a_very_secret_key"  # CHANGE THIS!
    ALGORITHM: str = "HS256"
    # Set to 30 days for family shopping app (users should stay logged in for weeks)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days = 30 * 24 * 60 minutes

    # OAuth Google
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None

    # OAuth Apple
    APPLE_OAUTH_CLIENT_ID: Optional[str] = None  # Usually your Bundle ID
    APPLE_OAUTH_TEAM_ID: Optional[str] = None
    APPLE_OAUTH_KEY_ID: Optional[str] = None
    APPLE_OAUTH_PRIVATE_KEY: Optional[str] = None  # The content of your .p8 key file

    # AI APIs
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL_NAME: str = (
        "gemini-2.5-flash-lite-preview-06-17"  # Cost-efficient model with low latency, supports text/images/video/audio
    )

    # AI Provider Configuration
    AI_PROVIDER: str = "gemini"  # Options: "gemini", "ollama"

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"  # Default Ollama server URL
    OLLAMA_MODEL_NAME: str = (
        "gemma3:4b"  # Default model for Ollama (matches available model)
    )
    OLLAMA_TIMEOUT: int = 120  # Request timeout in seconds

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @model_validator(mode="after")
    def get_redis_url(self) -> "Settings":
        if self.REDIS_PASSWORD:
            self.REDIS_URL = (
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
            )
        else:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return self

    # Email Service Configuration
    EMAIL_PROVIDER: str = "console"  # Options: "brevo", "resend", "smtp", "console"
    EMAIL_ENABLED: bool = True  # Set to False to disable all email sending

    # Brevo Configuration (formerly Sendinblue)
    BREVO_API_KEY: Optional[str] = None
    BREVO_SMTP_HOST: str = "smtp-relay.brevo.com"
    BREVO_SMTP_PORT: int = 587
    BREVO_SMTP_USER: Optional[str] = None
    BREVO_SMTP_PASSWORD: Optional[str] = None

    # Generic SMTP Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = False
    SMTP_START_TLS: bool = True

    # Email Settings
    FROM_EMAIL: str = "noreply@familycart.com"
    FROM_NAME: str = "FamilyCart"
    SUPPORT_EMAIL: str = "support@familycart.com"

    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"

    # Email Token Expiration (for fastapi-users compatibility)
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48  # 2 days
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1  # 1 hour for security
    INVITATION_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    
    # Token lifetime in seconds (for compatibility with fastapi-users)
    VERIFICATION_TOKEN_LIFETIME_SECONDS: int = 172800  # 48 hours
    RESET_PASSWORD_TOKEN_LIFETIME_SECONDS: int = 3600  # 1 hour
    INVITATION_TOKEN_LIFETIME_SECONDS: int = 604800  # 7 days

    class Config:
        # Pydantic-settings will automatically load environment variables from the .env file.
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
