"""
CORS middleware for handling cross-origin requests properly.
This is important to ensure proper behavior with modern browsers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Set up CORS middleware to allow cross-origin requests.
    This is essential for the frontend to be able to communicate with the API.
    """
    origins = [
        "http://localhost:3000",  # Next.js development server
        "http://localhost:8000",  # Backend itself (for debug pages)
        "http://localhost",  # Generic localhost
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:8000",  # Alternative localhost for backend
        "*",  # Allow all origins for development (restrict in production)
    ]

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
