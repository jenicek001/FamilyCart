# User /me Endpoint Fix

## Problem
The FastAPI backend had a path routing issue where the `/api/v1/users/me` endpoint was not properly configured, resulting in a 404 error when the frontend tried to access it.

## Root Cause
In the users router configuration, there was a double prefix issue. The router in `app/api/v1/endpoints/users.py` had an explicit prefix `/users`, and the included fastapi-users router also had a prefix `/users`. This resulted in the endpoint being available at `/api/v1/users/users/me` instead of the expected `/api/v1/users/me`.

## Fix
1. Modified `app/api/v1/endpoints/users.py` to correctly set up the router:
   - Changed the main router to have a `/users` prefix
   - Removed the prefix from the included fastapi-users router

This ensures the endpoint is available at the correct path `/api/v1/users/me` that the frontend expects.
