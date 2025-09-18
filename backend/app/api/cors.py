"""
CORS middleware for handling cross-origin requests properly.
This is important to ensure proper behavior with modern browsers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Set up CORS middleware to allow cross-origin requests.
    This is essential for the frontend to be able to communicate with the API.
    """
    # Build backend URLs from configuration
    backend_urls = [
        f"http://localhost:{settings.PORT}",  # Backend dev port
        f"http://127.0.0.1:{settings.PORT}",  # Alternative localhost for backend dev
    ]

    origins = [
        "http://localhost:3000",  # Next.js development server (UAT)
        "http://localhost:9002",  # Frontend dev port
        "http://127.0.0.1:3000",  # Alternative localhost (UAT)
        "http://127.0.0.1:9002",  # Alternative localhost for frontend dev
    ] + backend_urls

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Allow cookies in cross-origin requests
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"],  # Expose all response headers
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    logger.info("CORS middleware configured with origins: %s", origins)
