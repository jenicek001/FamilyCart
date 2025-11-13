import logging
import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from app.api.deps import get_user_db
from app.core.config import settings
from app.models.user import User
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages user authentication and operations."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Request | None = None):
        """
        Called after a user successfully registers.
        Sends verification email automatically.
        """
        logger.info(f"User {user.id} ({user.email}) has registered.")

        # Generate verification token and send email
        try:
            token = await self.request_verify(user, request)
            logger.info(
                f"Verification email automatically sent to {user.email} with token"
            )
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            # Don't block registration if email fails

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        """
        Called after a password reset is requested.
        Sends password reset email with token.
        """
        logger.info(f"User {user.id} ({user.email}) requested password reset.")

        try:
            email_service = get_email_service()
            await email_service.send_password_reset_email(
                recipient=user.email,
                token=token,
            )
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {e}")
            # Don't block password reset flow if email fails

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        """
        Called after email verification is requested.
        Sends verification email with token.
        """
        logger.info(f"Verification requested for user {user.id} ({user.email}).")

        try:
            email_service = get_email_service()
            await email_service.send_verification_email(
                recipient=user.email,
                token=token,
            )
            logger.info(f"Verification email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            # Don't block verification flow if email fails


async def get_user_manager(user_db=Depends(get_user_db)):
    """
    Dependency to get the user manager.
    """
    yield UserManager(user_db)
