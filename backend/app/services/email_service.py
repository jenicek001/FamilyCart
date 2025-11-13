"""
Email Service Module

Provides centralized email sending functionality with multiple provider support.
Implements async email sending using aiosmtplib and Jinja2 template rendering.

Supported providers:
- Console: Development mode (prints emails to console)
- Brevo (Sendinblue): Production SMTP provider
- SMTP: Generic SMTP server support
"""

import logging
from abc import ABC, abstractmethod
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Dict, Any
import aiosmtplib
from email_validator import validate_email, EmailNotValidError
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)

# Template directory configuration
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class EmailProvider(ABC):
    """Abstract base class for email providers"""
    
    @abstractmethod
    async def send_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email message
        
        Args:
            recipient: Email address of the recipient
            subject: Email subject line
            html_content: HTML content of the email
            text_content: Optional plain text content
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        pass


class ConsoleEmailProvider(EmailProvider):
    """Console email provider for development - prints emails to console"""
    
    async def send_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Print email to console instead of sending"""
        logger.info("=" * 80)
        logger.info("CONSOLE EMAIL PROVIDER - EMAIL OUTPUT")
        logger.info("=" * 80)
        logger.info(f"To: {recipient}")
        logger.info(f"From: {settings.FROM_EMAIL}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 80)
        if text_content:
            logger.info("Plain Text Content:")
            logger.info(text_content)
            logger.info("-" * 80)
        logger.info("HTML Content:")
        logger.info(html_content)
        logger.info("=" * 80)
        return True


class SMTPEmailProvider(EmailProvider):
    """
    SMTP email provider using aiosmtplib
    
    Supports Brevo (Sendinblue) and generic SMTP servers with:
    - Async connection management
    - STARTTLS encryption
    - Authentication
    - Retry logic
    """
    
    def __init__(
        self,
        hostname: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = False,
        start_tls: bool = True,
        timeout: float = 60.0,
    ):
        """
        Initialize SMTP provider
        
        Args:
            hostname: SMTP server hostname
            port: SMTP server port (587 for STARTTLS, 465 for TLS, 25 for plain)
            username: SMTP authentication username
            password: SMTP authentication password
            use_tls: If True, connect directly over TLS/SSL (port 465)
            start_tls: If True, upgrade connection with STARTTLS (port 587)
            timeout: Timeout for socket operations in seconds
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.start_tls = start_tls
        self.timeout = timeout
    
    async def send_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send email via SMTP using aiosmtplib
        
        Based on official aiosmtplib documentation:
        - Uses async context manager for connection management
        - Supports both plain text and HTML multipart messages
        - Implements proper error handling
        """
        try:
            # Create email message
            message = EmailMessage()
            message["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
            message["To"] = recipient
            message["Subject"] = subject
            
            # Set content - prefer HTML with plain text fallback
            if text_content:
                message.set_content(text_content)
                message.add_alternative(html_content, subtype="html")
            else:
                message.set_content(html_content, subtype="html")
            
            # Send email using async context manager
            # This pattern from aiosmtplib docs automatically handles connect/disconnect
            async with aiosmtplib.SMTP(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
                start_tls=self.start_tls,
                timeout=self.timeout,
            ) as smtp:
                await smtp.send_message(message)
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {recipient}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient}: {str(e)}")
            return False


class EmailService:
    """
    Centralized email service with template rendering
    
    Features:
    - Multiple provider support (console, Brevo SMTP, generic SMTP)
    - Jinja2 template rendering with Family Warmth branding
    - Email validation using email-validator
    - Async/await support
    """
    
    def __init__(self):
        """Initialize email service with configured provider and Jinja2 environment"""
        self.provider = self._get_provider()
        
        # Initialize Jinja2 environment for email templates
        # Based on official Jinja2 documentation
        if TEMPLATES_DIR.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(TEMPLATES_DIR)),
                autoescape=select_autoescape(["html", "xml"]),
                enable_async=True,  # Enable async template rendering
            )
        else:
            logger.warning(f"Email templates directory not found: {TEMPLATES_DIR}")
            self.jinja_env = None
    
    def _get_provider(self) -> EmailProvider:
        """
        Factory method to create appropriate email provider
        
        Returns:
            EmailProvider: Configured email provider instance
        """
        provider_type = settings.EMAIL_PROVIDER.lower()
        
        if provider_type == "console":
            logger.info("Using Console email provider (development mode)")
            return ConsoleEmailProvider()
        
        elif provider_type == "brevo":
            logger.info("Using Brevo SMTP email provider")
            return SMTPEmailProvider(
                hostname=settings.BREVO_SMTP_HOST,
                port=settings.BREVO_SMTP_PORT,
                username=settings.BREVO_SMTP_USER,
                password=settings.BREVO_SMTP_PASSWORD,
                use_tls=False,  # Brevo uses STARTTLS on port 587
                start_tls=True,
                timeout=60.0,
            )
        
        elif provider_type == "smtp":
            logger.info("Using generic SMTP email provider")
            return SMTPEmailProvider(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
                start_tls=settings.SMTP_START_TLS,
                timeout=60.0,
            )
        
        else:
            logger.warning(f"Unknown email provider '{provider_type}', falling back to console")
            return ConsoleEmailProvider()
    
    def validate_email_address(self, email: str) -> Optional[str]:
        """
        Validate email address and return normalized form
        
        Uses email-validator library as per official documentation
        
        Args:
            email: Email address to validate
            
        Returns:
            Optional[str]: Normalized email address if valid, None otherwise
        """
        try:
            # Validate email with deliverability check disabled for performance
            # Based on official email-validator documentation
            email_info = validate_email(email, check_deliverability=False)
            return email_info.normalized
        except EmailNotValidError as e:
            logger.error(f"Invalid email address '{email}': {str(e)}")
            return None
    
    async def send_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email with validation
        
        Args:
            recipient: Email address of recipient
            subject: Email subject line
            html_content: HTML content of email
            text_content: Optional plain text content
            
        Returns:
            bool: True if email sent successfully
        """
        # Validate recipient email
        validated_email = self.validate_email_address(recipient)
        if not validated_email:
            logger.error(f"Cannot send email to invalid address: {recipient}")
            return False
        
        # Send email via configured provider
        return await self.provider.send_email(
            recipient=validated_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )
    
    async def send_template_email(
        self,
        recipient: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Send an email using a Jinja2 template
        
        Args:
            recipient: Email address of recipient
            subject: Email subject line
            template_name: Name of template file (e.g., 'verification.html')
            context: Dictionary of variables to pass to template
            
        Returns:
            bool: True if email sent successfully
        """
        if not self.jinja_env:
            logger.error("Cannot send template email: Jinja2 environment not initialized")
            return False
        
        try:
            # Load and render template
            # Based on official Jinja2 async rendering documentation
            template = self.jinja_env.get_template(template_name)
            html_content = await template.render_async(**context)
            
            # Send rendered email
            return await self.send_email(
                recipient=recipient,
                subject=subject,
                html_content=html_content,
            )
            
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {str(e)}")
            return False
    
    # Convenience methods for common email types
    
    async def send_verification_email(
        self,
        recipient: str,
        token: str,
    ) -> bool:
        """
        Send email verification email
        
        This will be called from fastapi-users on_after_request_verify hook
        
        Args:
            recipient: User's email address
            token: Verification token
            
        Returns:
            bool: True if email sent successfully
        """
        verification_url = f"{settings.FRONTEND_URL}/auth/verify?token={token}"
        
        context = {
            "verification_url": verification_url,
            "frontend_url": settings.FRONTEND_URL,
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject="Verify your FamilyCart email address",
            template_name="verification.html",
            context=context,
        )
    
    async def send_password_reset_email(
        self,
        recipient: str,
        token: str,
    ) -> bool:
        """
        Send password reset email
        
        This will be called from fastapi-users on_after_forgot_password hook
        
        Args:
            recipient: User's email address
            token: Password reset token
            
        Returns:
            bool: True if email sent successfully
        """
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        
        context = {
            "reset_url": reset_url,
            "frontend_url": settings.FRONTEND_URL,
            "expiry_hours": settings.RESET_PASSWORD_TOKEN_LIFETIME_SECONDS // 3600,
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject="Reset your FamilyCart password",
            template_name="password_reset.html",
            context=context,
        )
    
    async def send_invitation_email(
        self,
        recipient: str,
        inviter_name: str,
        list_name: str,
        list_id: Optional[str] = None,
        invitation_token: Optional[str] = None,
    ) -> bool:
        """
        Send shopping list invitation email
        
        Handles both existing users and new user invitations
        
        Args:
            recipient: Invitee's email address
            inviter_name: Name of person sending invitation
            list_name: Name of shopping list
            list_id: ID of the specific shopping list (for existing users)
            invitation_token: Token for new users (None for existing users)
            
        Returns:
            bool: True if email sent successfully
        """
        if invitation_token:
            # New user invitation with registration link (generic, not list-specific)
            invitation_url = f"{settings.FRONTEND_URL}/auth/register?invitation={invitation_token}"
            template_name = "invitation_new_user.html"
        else:
            # Existing user invitation - direct to specific list
            if list_id:
                invitation_url = f"{settings.FRONTEND_URL}/lists/{list_id}"
            else:
                # Fallback to generic lists page if no list_id provided
                invitation_url = f"{settings.FRONTEND_URL}/lists"
            template_name = "invitation_existing_user.html"
        
        context = {
            "inviter_name": inviter_name,
            "list_name": list_name,
            "invitation_url": invitation_url,
            "frontend_url": settings.FRONTEND_URL,
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject=f"{inviter_name} invited you to collaborate on {list_name}",
            template_name=template_name,
            context=context,
        )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get or create singleton email service instance
    
    Returns:
        EmailService: Singleton email service instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
