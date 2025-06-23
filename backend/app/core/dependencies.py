# backend/app/core/dependencies.py
from app.core.fastapi_users import fastapi_users

# This dependency is now defined in one place, breaking the circular import.
get_current_user = fastapi_users.current_user()
