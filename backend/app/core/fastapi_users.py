import uuid

from fastapi_users import FastAPIUsers

from app.core.auth import auth_backend
from app.core.users import get_user_manager
from app.models.user import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
