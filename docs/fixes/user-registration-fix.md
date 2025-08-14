# User Registration Fix

## Issue
- User registration POST request failed with a 404 Not Found error
- The frontend was making a request to `/api/v1/auth/register` but this endpoint wasn't properly configured

## Root Cause
There were two separate issues:

1. **Router Configuration Issue**:
   - Initially, the register router was included in `users.py` without a proper path prefix
   - We moved the registration routes to `auth.py` but the router prefix was incorrect
   - In `auth.py`, we had routes with path prefixes like `/register` but without a parent `/auth` prefix
   - In `main.py`, the auth router was included with only the API version prefix (`/api/v1`), resulting in paths like `/api/v1/register` instead of `/api/v1/auth/register`

2. **Database Model Relationship Issue**:
   - There was a mismatch between relationship definitions in the User and ShoppingList models
   - In `user.py`, we had `secondary="user_shopping_list_link"` (incorrect table name)
   - In `shopping_list.py`, we had `secondary=user_shopping_list` (correct table name)
   - The back_populates values were also mismatched between the models

## Solution

### Router Configuration Fix
1. Reorganized all auth-related routes in `auth.py` under a single router with an `/auth` prefix
   ```python
   router = APIRouter(prefix="/auth")  # Add /auth prefix to the entire router
   ```
2. Simplified the register endpoint to use the base path (no additional prefix needed since the parent router has the `/auth` prefix)
   ```python
   # Register routes - used by the frontend for signup
   router.include_router(
       fastapi_users.get_register_router(UserRead, UserCreate),
       tags=["auth"],
   )
   ```
3. Added proper prefixes for additional auth routes (jwt, reset-password, verify)

### Database Model Fix
1. Fixed the relationship definitions in the User model:
   ```python
   shared_lists: Mapped[List["ShoppingList"]] = relationship(
       secondary="user_shopping_list",  # Fixed: was "user_shopping_list_link"
       back_populates="shared_with"     # Fixed: was "shared_with_users"
   )
   ```
2. Fixed the owner relationship in the ShoppingList model:
   ```python
   owner: Mapped["User"] = relationship(back_populates="owned_shopping_lists")  # Fixed: was "shopping_lists"
   ```

### Verified Endpoints
- Registration: `/api/v1/auth/register` 
- Login: `/api/v1/auth/jwt/login`
- Password reset: `/api/v1/auth/reset-password/...`
- Email verification: `/api/v1/auth/verify/...`

## Testing
The user registration flow now works correctly:
1. Frontend makes a POST request to `/api/v1/auth/register` with user data
2. After successful registration, it logs in through `/api/v1/auth/jwt/login`
3. The user is redirected to the dashboard
