"""
FastAPI Prometheus Metrics Integration for FamilyCart Backend
============================================================

This script shows how to add Prometheus metrics to the FamilyCart FastAPI backend.
Add this code to your main FastAPI app setup.

Installation with Poetry 2.x:
    cd backend
    poetry add prometheus-client prometheus-fastapi-instrumentator

Usage:
    1. Add the imports and setup code to your app/main.py
    2. Rebuild your backend container
    3. Access metrics at http://localhost:8001/metrics
"""

# Add these imports to your app/main.py
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
import time
import os

# Custom metrics for FamilyCart
familycart_requests_total = Counter(
    'familycart_requests_total',
    'Total requests to FamilyCart API',
    ['method', 'endpoint', 'status']
)

familycart_response_time = Histogram(
    'familycart_response_time_seconds',
    'Response time for FamilyCart API requests',
    ['method', 'endpoint']
)

familycart_active_users = Gauge(
    'familycart_active_users_total',
    'Number of active WebSocket connections'
)

familycart_shopping_lists = Gauge(
    'familycart_shopping_lists_total',
    'Total number of shopping lists'
)

familycart_items = Gauge(
    'familycart_items_total',
    'Total number of shopping list items'
)

# WebSocket connections counter
websocket_connections = Gauge(
    'familycart_websocket_connections',
    'Current number of WebSocket connections'
)

# AI provider metrics
ai_requests_total = Counter(
    'familycart_ai_requests_total',
    'Total AI provider requests',
    ['provider', 'operation', 'status']
)

ai_response_time = Histogram(
    'familycart_ai_response_time_seconds',
    'AI provider response time',
    ['provider', 'operation']
)

# Database metrics
db_connections = Gauge(
    'familycart_db_connections_active',
    'Active database connections'
)

# Redis cache metrics
redis_operations = Counter(
    'familycart_redis_operations_total',
    'Total Redis cache operations',
    ['operation', 'status']
)


def setup_metrics(app):
    """
    Setup Prometheus metrics for FamilyCart FastAPI app
    
    Add this function call to your app initialization:
    
    # In app/main.py
    app = FastAPI(title="FamilyCart API", version="1.0.0")
    setup_metrics(app)  # Add this line
    """
    
    # Enable basic FastAPI metrics
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[".*admin.*", "/health", "/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="familycart_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Add custom metrics
    instrumentator.add(
        lambda info: familycart_requests_total.labels(
            method=info.method,
            endpoint=info.modified_handler,
            status=info.response.status_code
        ).inc()
    )
    
    instrumentator.add(
        lambda info: familycart_response_time.labels(
            method=info.method,
            endpoint=info.modified_handler
        ).observe(info.response.elapsed_time)
    )
    
    # Instrument the app
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
    
    # Custom middleware for additional metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        process_time = time.time() - start_time
        familycart_response_time.labels(
            method=request.method,
            endpoint=str(request.url.path)
        ).observe(process_time)
        
        return response
    
    return app


# WebSocket metrics helpers (add to your WebSocket manager)
def increment_websocket_connections():
    """Call when a WebSocket connects"""
    websocket_connections.inc()
    familycart_active_users.inc()

def decrement_websocket_connections():
    """Call when a WebSocket disconnects"""
    websocket_connections.dec()
    familycart_active_users.dec()


# Database metrics helpers (add to your database operations)
async def update_database_metrics(session):
    """Update database-related metrics"""
    from sqlalchemy import text
    
    try:
        # Count shopping lists
        result = await session.execute(text("SELECT COUNT(*) FROM shopping_lists"))
        familycart_shopping_lists.set(result.scalar())
        
        # Count items
        result = await session.execute(text("SELECT COUNT(*) FROM items"))
        familycart_items.set(result.scalar())
        
        # Active connections (PostgreSQL specific)
        result = await session.execute(text(
            "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
        ))
        db_connections.set(result.scalar())
        
    except Exception as e:
        print(f"Error updating database metrics: {e}")


# AI provider metrics helpers (add to your AI service calls)
def record_ai_request(provider: str, operation: str, success: bool, duration: float):
    """Record AI provider request metrics"""
    status = "success" if success else "error"
    ai_requests_total.labels(provider=provider, operation=operation, status=status).inc()
    ai_response_time.labels(provider=provider, operation=operation).observe(duration)


# Redis metrics helpers (add to your Redis operations)
def record_redis_operation(operation: str, success: bool):
    """Record Redis cache operation metrics"""
    status = "success" if success else "error" 
    redis_operations.labels(operation=operation, status=status).inc()


# Health check endpoint with metrics
async def metrics_health_check():
    """
    Custom health check that includes metrics status
    Add this to your health check endpoint
    """
    return {
        "status": "healthy",
        "metrics_enabled": os.getenv("ENABLE_METRICS", "false").lower() == "true",
        "metrics_endpoint": "/metrics",
        "monitoring": {
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3000",
            "alertmanager": "http://localhost:9093"
        }
    }


# Example integration in main.py:
"""
# Add to app/main.py

from app.monitoring.metrics import setup_metrics  # Import the setup function

# Create FastAPI app
app = FastAPI(
    title="FamilyCart API", 
    version="1.0.0",
    description="Shared Shopping List Application"
)

# Setup Prometheus metrics (if enabled)
if os.getenv("ENABLE_METRICS", "false").lower() == "true":
    setup_metrics(app)

# Your existing routes and middleware...
"""
