from fastapi import FastAPI
from app.api.v1.endpoints import auth as auth_v1_router
from app.api.v1.endpoints import users as users_v1_router
from app.api.v1.endpoints import shopping_lists as sl_v1_router
from app.api.v1.endpoints import shopping_lists_no_slash as sl_noslash_v1_router  # No trailing slash router
from app.api.v1.endpoints import items as items_v1_router
from app.api.v1.endpoints import ai as ai_v1_router  # Import the new AI router
from app.api.v1.ws import notifications as ws_v1_router # WebSocket router
from app.core.config import settings
from app.api.middleware import LoggingMiddleware
from app.api.auth_logging import AuthLoggingMiddleware
from app.api.cors import setup_cors_middleware  # Import CORS setup
import logging

# Configure detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Add custom middleware for better error logging
app.add_middleware(LoggingMiddleware)
# Add auth logging middleware
app.add_middleware(AuthLoggingMiddleware)
# Setup CORS middleware (needs to be added early in middleware chain)
setup_cors_middleware(app)

# Include v1 Routers
app.include_router(auth_v1_router.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users_v1_router.router, prefix=settings.API_V1_STR, tags=["users"])  # Removed the /users suffix as it's already included in the router paths

# Include both versions of the shopping-lists endpoint (with and without trailing slash)
# With trailing slash - primary endpoint
app.include_router(sl_v1_router.router, prefix=settings.API_V1_STR + "/shopping-lists", tags=["shopping_lists"])
# Without trailing slash - ensures no redirect is needed
app.include_router(sl_noslash_v1_router.router, prefix=settings.API_V1_STR + "/shopping-lists", tags=["shopping_lists"])

app.include_router(items_v1_router.router, prefix=settings.API_V1_STR + "/items", tags=["items"])
app.include_router(ai_v1_router.router, prefix=settings.API_V1_STR, tags=["ai"]) # Add the AI router

# Include WebSocket router for v1
app.include_router(ws_v1_router.router, prefix=settings.API_V1_STR + "/ws", tags=["websockets"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Shared Shopping List API"}
