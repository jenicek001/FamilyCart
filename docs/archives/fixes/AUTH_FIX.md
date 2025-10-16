# Authentication Fix for FamilyCart

## Issue Summary

The application was experiencing a 401 Unauthorized error when trying to access the `/api/v1/shopping-lists` endpoint. The issue was due to a mismatch in authentication methods:

- The backend was using `CookieTransport` for authentication
- The frontend was using Bearer token authentication

## The Fix

The solution was to update the backend to use `BearerTransport` instead of `CookieTransport`. This change makes the backend compatible with the token-based authentication already implemented in the frontend.

### Modified Files
- `/backend/app/core/auth.py`: Changed the authentication transport from `CookieTransport` to `BearerTransport`

## Testing the Fix

### Manual Testing
1. Restart the backend server:
   ```
   cd /path/to/FamilyCart/backend
   ./scripts/start.sh
   ```
   
   Note: Always use the `start.sh` script to run the backend as it ensures all database migrations are applied before starting the application.

2. Restart the frontend development server:
   ```
   cd /path/to/FamilyCart/frontend
   npm run dev
   ```

3. Sign up for a new account or login with an existing account
4. Navigate to the Dashboard or Profile page to verify that shopping lists load without errors

### Automated Test
A simple automated test script has been created to verify the authentication flow:

```
cd /path/to/FamilyCart/backend
python3 tests/test_auth_simple.py
```

This script tests:
1. User registration
2. User login and token retrieval
3. Access to protected shopping lists endpoint using the token
4. Verification that unauthorized access is properly blocked

## Additional Issues: Path Redirects and Authentication Headers

When making API requests to endpoints without a trailing slash (e.g., `/api/v1/shopping-lists`), FastAPI redirects to the version with a trailing slash (e.g., `/api/v1/shopping-lists/`). However, during this redirect, the authentication headers may not be preserved, resulting in 401 Unauthorized errors:

```
INFO:app.api.auth_logging:GET /api/v1/shopping-lists - Auth: Bearer eyJhbGci...
INFO:app.api.auth_logging:GET /api/v1/shopping-lists - Status: 307 - Took: 0.0005s
INFO:     127.0.0.1:43970 - "GET /api/v1/shopping-lists HTTP/1.1" 307 Temporary Redirect
INFO:app.api.auth_logging:GET /api/v1/shopping-lists/ - No Auth header
INFO:app.api.auth_logging:GET /api/v1/shopping-lists/ - Status: 401 - Took: 0.0027s
INFO:     127.0.0.1:43958 - "GET /api/v1/shopping-lists/ HTTP/1.1" 401 Unauthorized
```

### Problem Details

This is a common issue with browser-based applications and API redirects. When FastAPI redirects from a URL without a trailing slash to one with a trailing slash (307 Temporary Redirect), the browser may not forward the authentication headers in the redirected request. 

There are several aspects to this issue:

1. **FastAPI's redirect behavior**: FastAPI automatically redirects routes without trailing slashes to routes with trailing slashes.
2. **Browser behavior**: Browsers don't always preserve authentication headers during redirects for security reasons.
3. **Network request flow**: The client makes a request → server responds with 307 → client follows redirect without auth headers → server returns 401.

### Solution Implemented

We've implemented a multi-layered solution:

1. **Frontend URL Standardization**: The API client in `/frontend/src/lib/api.ts` has been updated to always add trailing slashes to API endpoints before making requests. This prevents the redirect from happening in the first place.

2. **Direct URL Usage**: All components have been updated to explicitly use trailing slashes in their API calls (e.g., `/api/v1/shopping-lists/` instead of `/api/v1/shopping-lists`).

3. **Special Handling for Problem URLs**: We've added special handling for problematic URLs in the API client interceptor that forces trailing slashes regardless of the original URL.

### Testing and Verification

To verify the fix and for future debugging, several tools have been created:

1. **Debug HTML Page**: Access `http://localhost:9002/debug-auth.html` to test authentication and API endpoints with and without trailing slashes.

2. **API Client Debug Page**: Access `http://localhost:9002/api-client-debug.html` to test URL transformations and make real API requests.

3. **Backend Logging**: The backend logs now include detailed authentication header information to help identify issues.

To properly debug any future issues, watch both the backend logs and browser network requests to ensure auth headers are properly sent and redirects are avoided.

## Future Improvements

1. Set up proper end-to-end testing with Playwright or similar tool
2. Add more comprehensive unit tests for authentication flows
3. Implement token refresh mechanism for better user experience
4. Consider adding monitoring for authentication failures with proper error reporting
5. Configure FastAPI to preserve authentication headers during redirects, if possible
