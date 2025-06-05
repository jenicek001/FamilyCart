from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    # first_name: str | None = None # Mirror custom fields
    # last_name: str | None = None
    pass

class UserCreate(schemas.BaseUserCreate):
    # first_name: str | None = None
    # last_name: str | None = None
    pass

class UserUpdate(schemas.BaseUserUpdate):
    # first_name: str | None = None
    # last_name: str | None = None
    pass
