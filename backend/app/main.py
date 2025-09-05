from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints import auth as auth_v1_router
from app.api.v1.endpoints import users as users_v1_router
from app.api.v1.endpoints import shopping_lists as sl_v1_router
from app.api.v1.endpoints import shopping_lists_no_slash as sl_noslash_v1_router  # No trailing slash router
from app.api.v1.endpoints import items as items_v1_router
from app.api.v1.endpoints import ai as ai_v1_router  # Import the new AI router
from app.api.v1.ws import notifications as ws_v1_router # WebSocket router
from app.core.config import settings
from app.core.cache import cache_service
from app.api.middleware import LoggingMiddleware
from app.api.auth_logging import AuthLoggingMiddleware
from app.api.cors import setup_cors_middleware  # Import CORS setup
from prometheus_fastapi_instrumentator import Instrumentator
import logging

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
    from app.services.websocket_service import websocket_service
    from app.api.v1.ws.notifications import connection_manager
    websocket_service.set_connection_manager(connection_manager)
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    await cache_service.close()
    logger.info("Application shutdown complete")

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

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

# Health check endpoint - required for Docker health checks and load testing
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 OK with service status information.
    """
    from datetime import datetime
    import os
    
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
                "available_memory_gb": round(memory_info.available / (1024**3), 2)
            }
            uptime_seconds = int((datetime.now() - datetime.fromtimestamp(psutil.Process(os.getpid()).create_time())).total_seconds())
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
                "environment": getattr(settings, 'ENVIRONMENT', 'unknown')
            },
            "checks": {
                "cache": cache_status,
                **system_info
            },
            "uptime_seconds": uptime_seconds
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return 503 Service Unavailable for serious health issues
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

# System information endpoint - detailed system metrics for monitoring
@app.get("/system/info")
async def system_info():
    """
    Detailed system information endpoint for monitoring and administration.
    Returns comprehensive system metrics and resource usage.
    """
    from datetime import datetime
    import os
    
    try:
        import psutil
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Disk usage for root partition
        disk = psutil.disk_usage('/')
        
        # Process information
        current_process = psutil.Process(os.getpid())
        process_memory = current_process.memory_info()
        
        # System uptime
        boot_time = psutil.boot_time()
        uptime_seconds = int((datetime.now().timestamp() - boot_time))
        
        system_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": {
                "name": settings.PROJECT_NAME,
                "version": "1.0.0",
                "environment": getattr(settings, 'ENVIRONMENT', 'production'),
                "pid": os.getpid()
            },
            "system": {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": round(memory.percent, 2)
                },
                "cpu": {
                    "usage_percent": round(cpu_percent, 2),
                    "count": cpu_count
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2)
                },
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": str(datetime.fromtimestamp(boot_time))
            },
            "process": {
                "memory_rss_mb": round(process_memory.rss / (1024**2), 2),
                "memory_vms_mb": round(process_memory.vms / (1024**2), 2),
                "cpu_percent": round(current_process.cpu_percent(), 2),
                "create_time": datetime.fromtimestamp(current_process.create_time()).isoformat() + "Z",
                "num_threads": current_process.num_threads()
            }
        }
        
        return system_data
        
    except ImportError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="psutil not available - system information cannot be gathered"
        )
    except Exception as e:
        logger.error(f"System info endpoint failed: {e}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to gather system information: {str(e)}"
        )

# Metrics summary endpoint for monitoring dashboard integration
@app.get("/metrics/summary")
async def metrics_summary():
    """
    Metrics summary endpoint that provides key metrics for dashboard integration.
    Aggregates important application and system metrics for monitoring.
    """
    from datetime import datetime
    import os
    
    try:
        # Get cache service metrics
        cache_status = "healthy"
        cache_info = {}
        try:
            await cache_service.ping()
            # Try to get cache info if available
            cache_info = {
                "status": "connected",
                "type": "redis"
            }
        except Exception as e:
            logger.warning(f"Cache service check failed: {e}")
            cache_status = "degraded"
            cache_info = {
                "status": "disconnected",
                "error": str(e)
            }
        
        # Get basic system metrics
        system_metrics = {}
        try:
            import psutil
            memory = psutil.virtual_memory()
            system_metrics = {
                "memory_usage_percent": round(memory.percent, 2),
                "cpu_usage_percent": round(psutil.cpu_percent(interval=0.1), 2),
                "disk_usage_percent": round((psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 2)
            }
        except Exception as e:
            logger.warning(f"Could not gather system metrics: {e}")
        
        summary_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": {
                "name": settings.PROJECT_NAME,
                "status": "operational",
                "version": "1.0.0",
                "environment": getattr(settings, 'ENVIRONMENT', 'production')
            },
            "cache": cache_info,
            "system": system_metrics,
            "endpoints": {
                "health": "/health",
                "system_info": "/system/info",
                "metrics": "/metrics",
                "api_docs": f"{settings.API_V1_STR}/docs"
            }
        }
        
        return summary_data
        
    except Exception as e:
        logger.error(f"Metrics summary endpoint failed: {e}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate metrics summary: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Shared Shopping List API"}
