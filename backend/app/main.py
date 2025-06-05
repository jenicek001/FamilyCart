from fastapi import FastAPI
from app.api.v1.routers import auth as auth_v1_router
from app.api.v1.routers import users as users_v1_router
from app.api.v1.routers import shopping_lists as sl_v1_router
from app.api.v1.routers import items as items_v1_router
from app.api.v1 import ws_v1 # WebSocket router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Include v1 Routers
app.include_router(auth_v1_router.router, prefix=settings.API_V1_STR, tags=["v1_auth"])
app.include_router(users_v1_router.router, prefix=settings.API_V1_STR + "/users", tags=["v1_users"])
app.include_router(sl_v1_router.router, prefix=settings.API_V1_STR + "/shopping-lists", tags=["v1_shopping_lists"])
app.include_router(items_v1_router.router, prefix=settings.API_V1_STR + "/items", tags=["v1_items"])

# Include WebSocket router for v1
app.include_router(ws_v1.router, prefix=settings.API_V1_STR + "/ws", tags=["v1_websockets"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Shared Shopping List API"}
