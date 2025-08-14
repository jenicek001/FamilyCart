from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

logger = logging.getLogger(__name__)

class AuthLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log authentication headers and requests paths
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log beginning of request
        path = request.url.path
        method = request.method
        
        # Only log interesting paths (API calls)
        if path.startswith('/api/'):
            start_time = time.time()
            
            # Log auth header if present
            auth_header = request.headers.get('Authorization', None)
            if auth_header:
                # Mask the token for security
                masked_auth = auth_header[:15] + '...' if len(auth_header) > 15 else auth_header
                logger.info(f"{method} {path} - Auth: {masked_auth}")
            else:
                logger.info(f"{method} {path} - No Auth header")
            
            # Process the request
            response = await call_next(request)
            
            # Log the response time and status code
            process_time = time.time() - start_time
            logger.info(f"{method} {path} - Status: {response.status_code} - Took: {process_time:.4f}s")
            
            return response
        else:
            # For non-API paths, just pass through without logging
            return await call_next(request)
