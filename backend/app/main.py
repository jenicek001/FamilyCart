import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.auth_logging import AuthLoggingMiddleware
from app.api.cors import setup_cors_middleware  # Import CORS setup
from app.api.middleware import LoggingMiddleware
from app.api.v1.endpoints import ai as ai_v1_router  # Import the new AI router
from app.api.v1.endpoints import auth as auth_v1_router
from app.api.v1.endpoints import items as items_v1_router
from app.api.v1.endpoints import shopping_lists as sl_v1_router
from app.api.v1.endpoints import (
    shopping_lists_no_slash as sl_noslash_v1_router,  # No trailing slash router
)
from app.api.v1.endpoints import users as users_v1_router
from app.api.v1.ws import notifications as ws_v1_router  # WebSocket router
from app.core.cache import cache_service
from app.core.config import settings

# Configure detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    Replaces the deprecated @app.on_event decorators.
    """
    # Startup
    await cache_service.setup()

    # Initialize WebSocket service with connection manager
    from app.api.v1.ws.notifications import connection_manager
    from app.services.websocket_service import websocket_service

    websocket_service.set_connection_manager(connection_manager)

    logger.info("Application startup complete")

    yield

    # Shutdown
    await cache_service.close()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Add Prometheus metrics instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Add custom middleware for better error logging
app.add_middleware(LoggingMiddleware)
# Add auth logging middleware
app.add_middleware(AuthLoggingMiddleware)
# Setup CORS middleware (needs to be added early in middleware chain)
setup_cors_middleware(app)

# Include v1 Routers
app.include_router(auth_v1_router.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(
    users_v1_router.router, prefix=settings.API_V1_STR, tags=["users"]
)  # Removed the /users suffix as it's already included in the router paths

# Include both versions of the shopping-lists endpoint (with and without trailing slash)
# With trailing slash - primary endpoint
app.include_router(
    sl_v1_router.router,
    prefix=settings.API_V1_STR + "/shopping-lists",
    tags=["shopping_lists"],
)
# Without trailing slash - ensures no redirect is needed
app.include_router(
    sl_noslash_v1_router.router,
    prefix=settings.API_V1_STR + "/shopping-lists",
    tags=["shopping_lists"],
)

app.include_router(
    items_v1_router.router, prefix=settings.API_V1_STR + "/items", tags=["items"]
)
app.include_router(
    ai_v1_router.router, prefix=settings.API_V1_STR, tags=["ai"]
)  # Add the AI router

# Include WebSocket router for v1
app.include_router(
    ws_v1_router.router, prefix=settings.API_V1_STR + "/ws", tags=["websockets"]
)


# Health check endpoint - required for Docker health checks and load testing
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 OK with service status information.
    """
    import os
    from datetime import datetime

    try:
        # Check cache service connection
        cache_status = "healthy"
        try:
            await cache_service.ping()
        except Exception as e:
            logger.warning(f"Cache service check failed: {e}")
            cache_status = "degraded"

        # Try to get system info, but don't fail if psutil is not available
        system_info = {}
        try:
            import psutil

            memory_info = psutil.virtual_memory()
            system_info = {
                "memory_usage_percent": round(memory_info.percent, 2),
                "available_memory_gb": round(memory_info.available / (1024**3), 2),
            }
            uptime_seconds = int(
                (
                    datetime.now()
                    - datetime.fromtimestamp(psutil.Process(os.getpid()).create_time())
                ).total_seconds()
            )
        except ImportError:
            logger.warning("psutil not available, system info will be limited")
            uptime_seconds = 0
        except Exception as e:
            logger.warning(f"Could not gather system info: {e}")
            uptime_seconds = 0

        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": {
                "name": settings.PROJECT_NAME,
                "version": "1.0.0",
                "environment": getattr(settings, "ENVIRONMENT", "unknown"),
            },
            "checks": {"cache": cache_status, **system_info},
            "uptime_seconds": uptime_seconds,
        }

        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return 503 Service Unavailable for serious health issues
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}",
        )


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Shared Shopping List API"}
