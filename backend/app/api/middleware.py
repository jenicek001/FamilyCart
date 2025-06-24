import logging
from fastapi import Request
import traceback
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            logger.error(f"Request path: {request.url.path}")
            logger.error(f"Request method: {request.method}")
            if hasattr(request, "headers"):
                logger.error(f"Request headers: {request.headers}")
            if hasattr(request, "query_params"):
                logger.error(f"Request query params: {request.query_params}")
            
            # Print traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
