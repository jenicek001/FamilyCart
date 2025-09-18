from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)

from app.core.config import settings


def get_jwt_strategy() -> JWTStrategy:
    # Set token lifetime to 30 days (30 * 24 * 60 * 60 = 2,592,000 seconds)
    # This is appropriate for a family shopping app where users should stay logged in
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=2592000)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
