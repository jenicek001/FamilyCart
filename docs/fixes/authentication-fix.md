# Authentication Fix for Shopping Lists API

## Issue Description
After login, the dashboard showed nothing (empty or loading state). Upon page reload, the API returned 401 Unauthorized errors for the shopping lists endpoints.

The issue can be seen in the logs:
```
INFO:     127.0.0.1:54742 - "GET /api/v1/users/me HTTP/1.1" 200 OK
INFO:     127.0.0.1:54746 - "GET /api/v1/shopping-lists HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:54762 - "GET /api/v1/shopping-lists/ HTTP/1.1" 401 Unauthorized
```

This indicates that the authentication was working for the `/users/me` endpoint but failing for the `/shopping-lists/` endpoint.

## Root Cause
The issue was caused by inconsistent authentication dependencies between different API routers:

1. In `users.py`, we were using `current_user` directly from `fastapi_users` module.
2. In `shopping_lists.py` and `items.py`, we were using `get_current_user` from `dependencies.py`.

Although both dependencies should theoretically handle authentication the same way, the inconsistency was causing authentication to fail for shopping list endpoints.

## Solution

### Fixed Authentication Dependencies
1. Updated both `shopping_lists.py` and `items.py` to use the same authentication mechanism as `users.py`:
   ```python
   from app.core.fastapi_users import current_user
   ```

2. Updated all endpoint definitions to use `current_user` instead of `get_current_user`:
   ```python
   current_user: User = Depends(current_user)
   ```

### Details of Changes
1. Modified imports in `shopping_lists.py` and `items.py` to import `current_user` from `app.core.fastapi_users`
2. Updated all endpoint handlers to use this consistent authentication dependency

## Testing
After applying these changes, the dashboard should now properly display shopping lists after login, and API requests to `/api/v1/shopping-lists/` should return 200 OK instead of 401 Unauthorized.

## Related Files
- `/backend/app/api/v1/endpoints/shopping_lists.py`
- `/backend/app/api/v1/endpoints/items.py`

## Impact
This change ensures consistent authentication handling across all API endpoints, allowing the frontend to properly fetch and display shopping lists after login.
