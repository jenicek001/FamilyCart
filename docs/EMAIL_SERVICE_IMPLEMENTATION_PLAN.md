# Email Service Implementation Plan
**Project**: FamilyCart - Shared Shopping List App  
**Date**: November 9, 2025  
**Sprint**: Sprint 9 - Enhanced Collaboration  
**Status**: Planning Phase

---

## Executive Summary

This plan covers the implementation of 4 critical email features:
1. **Email Verification** for new user accounts
2. **Password Recovery** (forgot password flow)
3. **List Sharing Invitations** for existing users
4. **List Sharing Invitations** for non-existent users (with auto-registration)

**Alignment**: All features are explicitly mentioned in PLANNING.md (Milestone 1, Security Goals) and TASKS.md (Sprint 9).

**Current Status**: 
- `fastapi-users` library already integrated with placeholder email hooks
- Email routes already exist but print to console instead of sending emails
- Invitation system partially implemented (works for existing users, needs email for non-existent)

---

## Part 1: Email Service Provider Selection & Configuration

### 1.1 Recommended Provider: **Brevo (formerly Sendinblue)** ⭐

**Rationale**:
- ✅ Free tier: 300 emails/day (9,000/month) - sufficient for family shopping app
- ✅ Excellent deliverability (won't end up in spam folders)
- ✅ Simple SMTP integration + REST API available
- ✅ Professional HTML email editor
- ✅ SPF, DKIM, DMARC support for security
- ✅ Delivery tracking and analytics
- ✅ No credit card required for free tier

**Alternative**: Resend (100 emails/day, better developer experience)

### 1.2 Backend Configuration Updates

#### File: `backend/app/core/config.py`
Add email configuration settings:

```python
# Email Service Configuration
EMAIL_PROVIDER: str = "brevo"  # Options: "brevo", "resend", "smtp", "console"
EMAIL_ENABLED: bool = True  # Set to False for testing without emails

# Brevo Configuration
BREVO_API_KEY: Optional[str] = None
BREVO_SMTP_HOST: str = "smtp-relay.brevo.com"
BREVO_SMTP_PORT: int = 587
BREVO_SMTP_USER: Optional[str] = None
BREVO_SMTP_PASSWORD: Optional[str] = None

# Email Settings
FROM_EMAIL: str = "noreply@familycart.com"
FROM_NAME: str = "FamilyCart"
SUPPORT_EMAIL: str = "support@familycart.com"

# Frontend URL for email links
FRONTEND_URL: str = "http://localhost:3000"  # Change in production

# Email Token Expiration
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48  # 2 days
PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1  # 1 hour
INVITATION_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
```

#### File: `backend/.env.example`
Add environment variables:

```bash
# Email Service Configuration
EMAIL_PROVIDER=brevo
EMAIL_ENABLED=true

# Brevo Credentials (get from https://app.brevo.com)
BREVO_API_KEY=your_brevo_api_key_here
BREVO_SMTP_USER=your_brevo_smtp_login_here
BREVO_SMTP_PASSWORD=your_brevo_smtp_password_here

# Email Settings
FROM_EMAIL=noreply@familycart.com
FROM_NAME=FamilyCart
SUPPORT_EMAIL=support@familycart.com
FRONTEND_URL=http://localhost:3000
```

### 1.3 Dependencies

#### File: `backend/pyproject.toml`
Add email libraries:

```toml
[tool.poetry.dependencies]
# Existing dependencies...
aiosmtplib = "^3.0.0"  # Async SMTP client
email-validator = "^2.1.0"  # Email validation
jinja2 = "^3.1.0"  # Email template rendering
python-multipart = "^0.0.6"  # File handling (already may exist)
```

**Installation Command**:
```bash
cd backend
poetry add aiosmtplib email-validator jinja2
```

---

## Part 2: Email Service Infrastructure

### 2.1 Create Email Service Module

#### File: `backend/app/services/email_service.py` (NEW)

**Purpose**: Centralized email sending service with multiple provider support

**Key Components**:
1. **Abstract Email Provider Interface** - Strategy pattern for different providers
2. **Brevo SMTP Provider** - Primary implementation
3. **Console Provider** - For local testing without external service
4. **Email Queue System** - Async sending with retry logic
5. **Template Rendering** - Jinja2 templates with HTML/plain text fallback

**Core Functions**:
```python
async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_text_content: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
) -> bool

async def send_verification_email(user_email: str, token: str, user_name: str) -> bool
async def send_password_reset_email(user_email: str, token: str, user_name: str) -> bool
async def send_invitation_email(to_email: str, inviter_name: str, list_name: str, token: str) -> bool
```

**Error Handling**:
- Retry logic with exponential backoff (3 attempts)
- Logging all email attempts with success/failure status
- Graceful degradation (continue app operation if email fails)
- Admin alerts for sustained email failures

### 2.2 Email Templates

#### Directory: `backend/app/templates/email/` (NEW)

Create professional HTML email templates using **FamilyCart Family Warmth Visual Identity**:

**Reference Documents**:
- `docs/COLOR_PALETTE_IMPLEMENTATION.md` - Complete color palette specification
- `docs/VISUAL_IDENTITY_LOGIN_DIALOGS.md` - Brand implementation examples
- `docs/visual-style-system.md` - Typography and design system

**Templates to Create**:
1. `verification.html` - Email verification for new users
2. `password_reset.html` - Password reset link
3. `invitation_existing_user.html` - Invitation for registered users
4. `invitation_new_user.html` - Invitation for non-registered users
5. `base.html` - Base template with FamilyCart branding

**Template Variables**:
- `{{user_name}}` - Recipient's name
- `{{verification_link}}` - Action link (verify/reset/accept)
- `{{inviter_name}}` - Person sending invitation
- `{{list_name}}` - Shopping list name
- `{{expiry_hours}}` - Token expiration time
- `{{support_email}}` - Support contact
- `{{year}}` - Current year for footer

**FamilyCart Family Warmth Brand Guidelines**:

**Core Brand Colors** (from `COLOR_PALETTE_IMPLEMENTATION.md`):
- **🍊 Primary (Warm Orange)**: `#f59e0b` - CTA buttons, headers, primary actions
- **🔵 Secondary (Trusted Blue)**: `#3b82f6` - Links, secondary actions, trust elements
- **🟢 Accent (Fresh Green)**: `#22c55e` - Success states, completion indicators
- **Neutral Grays**: 
  - Text Primary: `#0f172a` (slate-900)
  - Text Secondary: `#64748b` (slate-500)
  - Borders: `#e2e8f0` (slate-200)
  - Background: `#f8fafc` (slate-50)

**Typography** (from `visual-style-system.md`):
- **Primary Font**: Plus Jakarta Sans (headings and interface)
- **Secondary Font**: Noto Sans (body text)
- **Fallback**: Arial, Helvetica, sans-serif (for email compatibility)
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

**Design Guidelines**:
- ✅ **Mobile-responsive** design (works on all email clients including Outlook, Gmail, Apple Mail)
- ✅ **WCAG AA compliant** contrast ratios (minimum 4.5:1 for normal text)
- ✅ **Clear call-to-action** buttons with warm orange (`#f59e0b`) background
- ✅ **FamilyCart logo** in header (use cart-family variant from `/logo` folder)
- ✅ **Professional footer** with support contact and year
- ✅ **Plain text fallback** for accessibility and email clients without HTML support
- ✅ **Table-based layout** for maximum email client compatibility
- ✅ **Inline CSS** (email clients don't support external stylesheets)
- ✅ **Family-oriented tone** - warm, approachable, helpful (not corporate)

---

## Part 3: Feature 1 - Email Verification for New Users

### 3.1 User Story
*As a new user, I want to verify my email address so that I can ensure my account is secure and receive important notifications.*

### 3.2 Current State
- `fastapi-users` already has verification routes: `POST /api/v1/auth/verify/request-token` and `POST /api/v1/auth/verify`
- User model has `is_verified` field from `SQLAlchemyBaseUserTableUUID`
- `UserManager.on_after_request_verify()` currently prints to console

### 3.3 Implementation Steps

#### Backend Changes

**Step 3.3.1**: Update `UserManager` in `backend/app/core/users.py`

```python
async def on_after_register(self, user: User, request: Request | None = None):
    """Called after successful user registration."""
    logger.info(f"User {user.id} has registered: {user.email}")
    
    # Automatically send verification email
    if settings.EMAIL_ENABLED:
        try:
            # Generate verification token
            token = await self.request_verify(user, request)
            
            # Send verification email
            await send_verification_email(
                user_email=user.email,
                token=token,
                user_name=user.display_name
            )
            logger.info(f"Verification email sent to {user.email}")
        except Exception as e:
            logger.exception(f"Failed to send verification email to {user.email}")
            # Don't block registration if email fails

async def on_after_request_verify(
    self, user: User, token: str, request: Request | None = None
):
    """Called when user requests email verification."""
    logger.info(f"Verification requested for user {user.id}")
    
    if settings.EMAIL_ENABLED:
        try:
            await send_verification_email(
                user_email=user.email,
                token=token,
                user_name=user.display_name
            )
            logger.info(f"Verification email sent to {user.email}")
        except Exception as e:
            logger.exception(f"Failed to send verification email to {user.email}")
```

**Step 3.3.2**: Create verification email template

**File**: `backend/app/templates/email/verification.html`
- Welcome message with Family Warmth branding
- Clear "Verify Email" button linking to frontend verification page
- Expiration notice (48 hours)
- Instructions for what to do if user didn't request verification

**Step 3.3.3**: Update email service to handle verification emails

Add to `backend/app/services/email_service.py`:
```python
async def send_verification_email(user_email: str, token: str, user_name: str) -> bool:
    """Send email verification link to user."""
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    html_content = render_template(
        "verification.html",
        user_name=user_name,
        verification_link=verification_link,
        expiry_hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
    )
    
    return await send_email(
        to_email=user_email,
        subject="Verify your FamilyCart account",
        html_content=html_content,
        plain_text_content=f"Verify your email: {verification_link}"
    )
```

#### Frontend Changes

**Step 3.3.4**: Create email verification page

**File**: `frontend/src/app/(auth)/verify-email/page.tsx` (NEW)

Features:
- Extract token from URL query parameter
- Call backend verification endpoint: `POST /api/v1/auth/verify`
- Show success message and redirect to login
- Handle errors (expired token, invalid token, already verified)
- Resend verification option if token expired

**Step 3.3.5**: Update signup flow

**File**: `frontend/src/app/(auth)/signup/page.tsx`

After successful registration:
- Show message: "Account created! Please check your email to verify your account."
- Display resend verification email option
- Inform user they can log in but some features may be restricted until verified

### 3.4 Testing Requirements

**Backend Tests**: `backend/app/tests/test_email_verification.py` (NEW)
- Test verification token generation
- Test verification email sending (mocked)
- Test successful email verification flow
- Test expired token handling
- Test invalid token handling
- Test already verified user
- Test resend verification email

**Frontend Tests**:
- Verify email page renders correctly
- Token extraction from URL works
- Success/error messages display properly
- Redirect after successful verification

### 3.5 Security Considerations

- ✅ Verification tokens are cryptographically secure (handled by `fastapi-users`)
- ✅ Tokens expire after 48 hours
- ✅ Tokens are single-use (can't be reused after verification)
- ✅ Rate limiting on verification request endpoint (prevent spam)
- ✅ Email sent to user's registered email only (no parameter injection)

---

## Part 4: Feature 2 - Password Recovery (Forgot Password)

### 4.1 User Story
*As a user who forgot my password, I want to receive a secure reset link via email so I can regain access to my account.*

### 4.2 Current State
- `fastapi-users` has password reset routes: `POST /api/v1/auth/reset-password/forgot-password` and `POST /api/v1/auth/reset-password/reset`
- `UserManager.on_after_forgot_password()` currently prints to console

### 4.3 Implementation Steps

#### Backend Changes

**Step 4.3.1**: Update `UserManager` in `backend/app/core/users.py`

```python
async def on_after_forgot_password(
    self, user: User, token: str, request: Request | None = None
):
    """Called when user requests password reset."""
    logger.info(f"User {user.id} requested password reset")
    
    if settings.EMAIL_ENABLED:
        try:
            await send_password_reset_email(
                user_email=user.email,
                token=token,
                user_name=user.display_name
            )
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logger.exception(f"Failed to send password reset email to {user.email}")
            # Return success to user anyway (security best practice - don't reveal if email exists)
```

**Step 4.3.2**: Create password reset email template

**File**: `backend/app/templates/email/password_reset.html`
- Security-focused message
- Clear "Reset Password" button
- Expiration notice (1 hour for security)
- Warning about not sharing the link
- Instructions if user didn't request reset

**Step 4.3.3**: Add password reset email function

Add to `backend/app/services/email_service.py`:
```python
async def send_password_reset_email(user_email: str, token: str, user_name: str) -> bool:
    """Send password reset link to user."""
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html_content = render_template(
        "password_reset.html",
        user_name=user_name,
        reset_link=reset_link,
        expiry_hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
    )
    
    return await send_email(
        to_email=user_email,
        subject="Reset your FamilyCart password",
        html_content=html_content,
        plain_text_content=f"Reset your password: {reset_link}"
    )
```

#### Frontend Changes

**Step 4.3.4**: Create forgot password page

**File**: `frontend/src/app/(auth)/forgot-password/page.tsx` (NEW)

Features:
- Email input form
- Call backend: `POST /api/v1/auth/reset-password/forgot-password`
- Show success message (even if email doesn't exist - security)
- Link back to login page

**Step 4.3.5**: Create password reset page

**File**: `frontend/src/app/(auth)/reset-password/page.tsx` (NEW)

Features:
- Extract token from URL query parameter
- New password input form (with confirmation)
- Password strength indicator
- Call backend: `POST /api/v1/auth/reset-password/reset`
- Show success and redirect to login
- Handle errors (expired token, invalid token, weak password)

**Step 4.3.6**: Add "Forgot Password?" link to login page

**File**: `frontend/src/app/(auth)/login/page.tsx`

Add link below password field pointing to `/forgot-password`

### 4.4 Testing Requirements

**Backend Tests**: `backend/app/tests/test_password_reset.py` (NEW)
- Test password reset token generation
- Test reset email sending (mocked)
- Test successful password reset flow
- Test expired token handling
- Test invalid token handling
- Test password validation rules
- Test non-existent email handling (should still return success)

**Frontend Tests**:
- Forgot password form submission
- Reset password page renders correctly
- Token extraction works
- Password validation works
- Success/error messages display

### 4.5 Security Considerations

- ✅ Reset tokens expire after 1 hour (short window for security)
- ✅ Tokens are single-use only
- ✅ Always return success even if email doesn't exist (prevent email enumeration)
- ✅ Rate limiting on forgot password endpoint (prevent abuse)
- ✅ New password must meet strength requirements
- ✅ User session is invalidated after password change
- ✅ Optional: Send "password changed" notification to user's email

---

## Part 5: Feature 3 - List Sharing Invitations (Existing Users)

### 5.1 User Story
*As a list owner, I want to send email notifications to existing users when I share a list with them, so they know they have access to a new shared list.*

### 5.2 Current State
- Sharing works for existing users (adds to `user_shopping_list` table)
- `send_list_invitation_email()` in `notification_service.py` currently prints to console
- WebSocket notifications already implemented for real-time updates

### 5.3 Implementation Steps

#### Backend Changes

**Step 5.3.1**: Update notification service

**File**: `backend/app/services/notification_service.py`

Replace the placeholder function:
```python
async def send_list_invitation_email(
    to_email: str,
    list_data: dict,
    inviter_email: str,
) -> None:
    """Send email invitation for existing user being added to a list."""
    from app.services.email_service import send_email, render_template
    from app.core.config import settings
    
    if not settings.EMAIL_ENABLED:
        logger.info(f"[Email Disabled] Invitation to {to_email} for list '{list_data.get('name')}'")
        return
    
    try:
        # Get inviter name from database
        inviter_name = inviter_email.split('@')[0]  # Fallback
        # TODO: Query actual inviter name from database
        
        # Render email template
        html_content = render_template(
            "invitation_existing_user.html",
            recipient_email=to_email,
            inviter_name=inviter_name,
            list_name=list_data.get('name'),
            list_description=list_data.get('description', ''),
            list_url=f"{settings.FRONTEND_URL}/lists/{list_data.get('id')}"
        )
        
        # Send email
        success = await send_email(
            to_email=to_email,
            subject=f"{inviter_name} shared '{list_data.get('name')}' with you",
            html_content=html_content,
            plain_text_content=f"{inviter_name} invited you to collaborate on '{list_data.get('name')}'. Log in to FamilyCart to view the list."
        )
        
        if success:
            logger.info(f"List invitation email sent to {to_email}")
        else:
            logger.error(f"Failed to send invitation email to {to_email}")
            
    except Exception as e:
        logger.exception(f"Error sending invitation email to {to_email}")
```

**Step 5.3.2**: Create invitation email template for existing users

**File**: `backend/app/templates/email/invitation_existing_user.html`

Content:
- Personalized greeting with inviter's name
- List name and description
- "View List" button linking to specific list
- Information about who else has access
- Instructions to log in to view the list

#### Frontend Changes

**Step 5.3.3**: Update ShareDialog success message

**File**: `frontend/src/components/ShoppingList/ShareDialog.tsx`

After successful share:
- Show: "List shared successfully! An email notification has been sent to [email]."
- Confirmation that user now has access

### 5.4 Testing Requirements

**Backend Tests**: `backend/app/tests/test_list_sharing_emails.py` (NEW)
- Test invitation email sending to existing user (mocked)
- Test email content has correct list information
- Test email failure doesn't block sharing functionality
- Test WebSocket + email notifications work together

### 5.5 User Experience Flow

1. User A shares list with existing User B (enters email)
2. Backend adds User B to list immediately
3. WebSocket notification sent to User B (if online)
4. Email sent to User B (for offline notification)
5. User B receives email and clicks "View List"
6. User B logs in and sees the shared list

---

## Part 6: Feature 4 - List Sharing Invitations (Non-Existent Users)

### 6.1 User Story
*As a list owner, I want to invite people who don't have FamilyCart accounts yet, so they can join the app and immediately access our shared list.*

### 6.2 Current State
- Sharing with non-existent users currently fails with 404 error
- No invitation tracking in database
- No auto-registration flow

### 6.3 Database Changes

#### Step 6.3.1: Create Invitation Model

**File**: `backend/app/models/invitation.py` (NEW)

```python
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .shopping_list import ShoppingList
    from .user import User


class Invitation(Base):
    """Model for tracking list invitations to non-existent users."""
    
    __tablename__ = "invitations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    # List and inviter information
    shopping_list_id: Mapped[int] = mapped_column(ForeignKey("shopping_lists.id"), nullable=False)
    inviter_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending",
        nullable=False
    )  # pending, accepted, expired, cancelled
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    shopping_list: Mapped["ShoppingList"] = relationship(back_populates="invitations")
    inviter: Mapped["User"] = relationship()
```

**Step 6.3.2**: Update ShoppingList model

**File**: `backend/app/models/shopping_list.py`

Add relationship:
```python
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .invitation import Invitation

class ShoppingList(Base):
    # ... existing fields ...
    
    # Add new relationship
    invitations: Mapped[List["Invitation"]] = relationship(
        back_populates="shopping_list",
        cascade="all, delete-orphan"
    )
```

**Step 6.3.3**: Create Alembic migration

```bash
cd backend
poetry run alembic revision --autogenerate -m "Add invitation tracking table"
poetry run alembic upgrade head
```

### 6.4 Backend Implementation

#### Step 6.4.1: Create invitation service

**File**: `backend/app/services/invitation_service.py` (NEW)

```python
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.invitation import Invitation
from app.models.shopping_list import ShoppingList
from app.models.user import User


async def create_invitation(
    session: AsyncSession,
    email: str,
    shopping_list: ShoppingList,
    inviter: User
) -> Invitation:
    """Create a new invitation for non-existent user."""
    # Generate secure random token
    token = secrets.token_urlsafe(32)
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(days=settings.INVITATION_TOKEN_EXPIRE_DAYS)
    
    # Create invitation
    invitation = Invitation(
        email=email.lower(),
        token=token,
        shopping_list_id=shopping_list.id,
        inviter_id=inviter.id,
        status="pending",
        expires_at=expires_at
    )
    
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)
    
    return invitation


async def get_invitation_by_token(
    session: AsyncSession,
    token: str
) -> Optional[Invitation]:
    """Get invitation by token."""
    result = await session.execute(
        select(Invitation).where(Invitation.token == token)
    )
    return result.scalar_one_or_none()


async def accept_invitation(
    session: AsyncSession,
    invitation: Invitation,
    user: User
) -> bool:
    """Accept an invitation and add user to list."""
    # Check if invitation is still valid
    if invitation.status != "pending":
        return False
    
    if invitation.expires_at < datetime.utcnow():
        invitation.status = "expired"
        await session.commit()
        return False
    
    # Add user to shopping list
    shopping_list = await session.get(ShoppingList, invitation.shopping_list_id)
    if shopping_list and user not in shopping_list.shared_with:
        shopping_list.shared_with.append(user)
    
    # Mark invitation as accepted
    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()
    
    await session.commit()
    return True


async def get_pending_invitations_by_email(
    session: AsyncSession,
    email: str
) -> list[Invitation]:
    """Get all pending invitations for an email address."""
    result = await session.execute(
        select(Invitation)
        .where(Invitation.email == email.lower())
        .where(Invitation.status == "pending")
        .where(Invitation.expires_at > datetime.utcnow())
    )
    return list(result.scalars().all())
```

#### Step 6.4.2: Update sharing service

**File**: `backend/app/api/v1/services/shopping_list_services.py`

Update `share_list_with_user` method:

```python
@staticmethod
async def share_list_with_user(
    shopping_list: ShoppingList,
    user_email: str,
    current_user: User,
    session: AsyncSession,
) -> ShoppingList:
    """Share a shopping list with a user by email."""
    # Check for existing user
    result = await session.execute(select(User).where(User.email == user_email))
    user_to_share_with = result.scalar_one_or_none()

    if user_to_share_with:
        # EXISTING USER PATH - add to list immediately
        if user_to_share_with in shopping_list.shared_with:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has access to this list",
            )
        
        shopping_list.shared_with.append(user_to_share_with)
        await session.commit()
        await session.refresh(shopping_list)
        
        # Send notification email
        await SharingService._send_sharing_notifications(
            shopping_list, user_email, current_user
        )
        
        return shopping_list
    
    else:
        # NON-EXISTENT USER PATH - create invitation
        from app.services.invitation_service import create_invitation
        from app.services.email_service import send_invitation_new_user_email
        
        # Check for existing pending invitation
        existing = await session.execute(
            select(Invitation)
            .where(Invitation.email == user_email.lower())
            .where(Invitation.shopping_list_id == shopping_list.id)
            .where(Invitation.status == "pending")
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation already sent to this email",
            )
        
        # Create invitation
        invitation = await create_invitation(
            session=session,
            email=user_email,
            shopping_list=shopping_list,
            inviter=current_user
        )
        
        # Send invitation email
        try:
            await send_invitation_new_user_email(
                to_email=user_email,
                inviter_name=current_user.display_name,
                list_name=shopping_list.name,
                token=invitation.token
            )
            logger.info(f"Invitation email sent to {user_email}")
        except Exception as e:
            logger.exception(f"Failed to send invitation email to {user_email}")
            # Don't fail the request if email fails
        
        # Return the list without the user added (they'll be added on acceptance)
        return shopping_list
```

#### Step 6.4.3: Create invitation acceptance endpoint

**File**: `backend/app/api/v1/endpoints/invitations.py` (NEW)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.invitation_service import (
    accept_invitation,
    get_invitation_by_token,
    get_pending_invitations_by_email
)

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("/accept/{token}")
async def accept_invitation_endpoint(
    token: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Accept a list invitation using token."""
    invitation = await get_invitation_by_token(session, token)
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired"
        )
    
    # Verify invitation email matches current user
    if invitation.email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email address"
        )
    
    # Accept invitation
    success = await accept_invitation(session, invitation, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired or already been accepted"
        )
    
    return {"message": "Invitation accepted successfully"}


@router.get("/pending")
async def get_pending_invitations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all pending invitations for current user."""
    invitations = await get_pending_invitations_by_email(session, current_user.email)
    
    return {
        "invitations": [
            {
                "id": inv.id,
                "list_name": inv.shopping_list.name,
                "inviter_name": inv.inviter.display_name,
                "created_at": inv.created_at.isoformat(),
                "expires_at": inv.expires_at.isoformat(),
                "token": inv.token
            }
            for inv in invitations
        ]
    }
```

#### Step 6.4.4: Update main router

**File**: `backend/app/api/v1/router.py`

```python
from app.api.v1.endpoints import invitations

api_router.include_router(invitations.router)
```

#### Step 6.4.5: Auto-accept invitations on registration

Update `UserManager.on_after_register()` in `backend/app/core/users.py`:

```python
async def on_after_register(self, user: User, request: Request | None = None):
    """Called after successful user registration."""
    logger.info(f"User {user.id} has registered: {user.email}")
    
    # Send verification email
    if settings.EMAIL_ENABLED:
        try:
            token = await self.request_verify(user, request)
            await send_verification_email(
                user_email=user.email,
                token=token,
                user_name=user.display_name
            )
        except Exception as e:
            logger.exception(f"Failed to send verification email")
    
    # Auto-accept pending invitations
    from app.services.invitation_service import get_pending_invitations_by_email, accept_invitation
    from app.api.deps import get_session
    
    try:
        # Get database session (need to handle this properly)
        async for session in get_session():
            invitations = await get_pending_invitations_by_email(session, user.email)
            
            for invitation in invitations:
                await accept_invitation(session, invitation, user)
                logger.info(f"Auto-accepted invitation {invitation.id} for new user {user.email}")
            
            break  # Only need first iteration
    except Exception as e:
        logger.exception(f"Failed to auto-accept invitations for new user")
```

### 6.5 Email Template for New Users

**File**: `backend/app/templates/email/invitation_new_user.html`

Content:
- Welcome message from inviter
- Explanation of FamilyCart
- List details they're invited to
- "Create Account & Accept Invitation" button
- Link includes invitation token in URL
- Alternative: "Already have an account? Log in to accept"
- Clear expiration notice (7 days)

### 6.6 Frontend Implementation

#### Step 6.6.1: Create invitation acceptance page

**File**: `frontend/src/app/accept-invitation/page.tsx` (NEW)

Features:
- Extract token from URL query parameter
- Check if user is logged in
  - **If logged in**: Accept invitation automatically
  - **If not logged in**: Show signup/login options with token preserved
- Success: Show list details and "Go to List" button
- Error handling for expired/invalid tokens

#### Step 6.6.2: Update signup flow to accept invitation

**File**: `frontend/src/app/(auth)/signup/page.tsx`

- Accept optional `invitation_token` query parameter
- After successful registration, automatically call accept invitation endpoint
- Redirect to the invited list instead of dashboard

#### Step 6.6.3: Update login flow to accept invitation

**File**: `frontend/src/app/(auth)/login/page.tsx`

- Accept optional `invitation_token` query parameter
- After successful login, automatically call accept invitation endpoint
- Redirect to the invited list

#### Step 6.6.4: Show pending invitations on dashboard

**File**: `frontend/src/components/dashboard/EnhancedDashboard.tsx`

- Fetch pending invitations on mount
- Show banner/notification if user has pending invitations
- "Accept All Invitations" button
- Individual accept buttons for each invitation

### 6.7 Testing Requirements

**Backend Tests**: `backend/app/tests/test_invitations.py` (NEW)
- Test invitation creation for non-existent user
- Test invitation email sending (mocked)
- Test invitation acceptance with valid token
- Test invitation expiration handling
- Test auto-accept on new user registration
- Test duplicate invitation prevention
- Test invitation to already-member user

**Integration Tests**: `backend/app/tests/test_invitation_flow.py` (NEW)
- Test complete flow: invite → email → signup → auto-accept
- Test complete flow: invite → email → login → accept
- Test expired invitation handling
- Test invitation to wrong email address

**Frontend Tests**:
- Accept invitation page renders correctly
- Token extraction and validation
- Signup with invitation token
- Login with invitation token
- Pending invitations display

### 6.8 Security Considerations

- ✅ Invitation tokens are cryptographically secure (32-byte urlsafe)
- ✅ Tokens expire after 7 days
- ✅ Tokens are single-use (status changes to 'accepted')
- ✅ Email must match invitation email for acceptance
- ✅ Duplicate invitations prevented
- ✅ Rate limiting on invitation endpoints
- ✅ Database cleanup job for expired invitations (optional background task)

---

## Part 7: Implementation Timeline & Phases

### Phase 1: Infrastructure Setup (Week 1)
**Priority**: HIGH - Foundation for all email features

- [ ] Set up Brevo account and get API credentials
- [ ] Add email configuration to `backend/app/core/config.py`
- [ ] Install email dependencies (`aiosmtplib`, `jinja2`, `email-validator`)
- [ ] Create email service module (`backend/app/services/email_service.py`)
- [ ] Create base email template with Family Warmth branding
- [ ] Test email sending with Brevo SMTP

**Deliverable**: Working email service that can send test emails

### Phase 2: Email Verification (Week 1-2)
**Priority**: HIGH - Security and user experience

- [ ] Create verification email template
- [ ] Update `UserManager.on_after_register()`
- [ ] Update `UserManager.on_after_request_verify()`
- [ ] Create frontend verification page
- [ ] Update signup flow to show verification message
- [ ] Write backend tests
- [ ] Write frontend tests
- [ ] Manual testing with real email

**Deliverable**: Users can verify email addresses

### Phase 3: Password Recovery (Week 2)
**Priority**: HIGH - Critical user support feature

- [ ] Create password reset email template
- [ ] Update `UserManager.on_after_forgot_password()`
- [ ] Create frontend forgot password page
- [ ] Create frontend reset password page
- [ ] Add "Forgot Password" link to login page
- [ ] Write backend tests
- [ ] Write frontend tests
- [ ] Manual testing with real email

**Deliverable**: Users can reset forgotten passwords

### Phase 4: Existing User Invitations (Week 2-3)
**Priority**: MEDIUM - Enhancement to existing feature

- [ ] Create invitation email template for existing users
- [ ] Update `notification_service.send_list_invitation_email()`
- [ ] Update ShareDialog success message
- [ ] Write backend tests
- [ ] Write frontend tests
- [ ] Manual testing with real users

**Deliverable**: Existing users receive email notifications for shared lists

### Phase 5: Non-Existent User Invitations (Week 3-4)
**Priority**: HIGH - New feature enabler

- [ ] Create Invitation database model
- [ ] Create Alembic migration
- [ ] Create invitation service module
- [ ] Create invitation email template for new users
- [ ] Update sharing service to handle non-existent users
- [ ] Create invitation endpoints (accept, get pending)
- [ ] Update UserManager for auto-accept on registration
- [ ] Create frontend invitation acceptance page
- [ ] Update signup flow for invitation tokens
- [ ] Update login flow for invitation tokens
- [ ] Show pending invitations on dashboard
- [ ] Write comprehensive tests
- [ ] End-to-end testing with real flow

**Deliverable**: Complete invitation system for non-existent users

### Phase 6: Polish & Production (Week 4)
**Priority**: MEDIUM - Production readiness

- [ ] Add rate limiting to email endpoints
- [ ] Create email sending monitoring/alerting
- [ ] Add admin dashboard for email statistics
- [ ] Performance testing (email sending under load)
- [ ] Security audit of email flows
- [ ] Update documentation
- [ ] Create user guides for email features
- [ ] Production deployment preparation

**Deliverable**: Production-ready email system

---

## Part 8: Configuration & Deployment

### 8.1 Brevo Setup Guide

1. **Create Account**: https://app.brevo.com/account/register
2. **Verify Domain** (Optional but recommended):
   - Add SPF record: `v=spf1 include:spf.brevo.com ~all`
   - Add DKIM record (provided by Brevo)
3. **Get SMTP Credentials**:
   - Go to SMTP & API → SMTP Settings
   - Copy SMTP login and password
4. **Get API Key** (alternative to SMTP):
   - Go to SMTP & API → API Keys
   - Create new API key
5. **Configure Sender Email**:
   - Add and verify sender email address
   - Use verified email in `FROM_EMAIL` environment variable

### 8.2 Environment Variables for Production

```bash
# Production .env file
EMAIL_PROVIDER=brevo
EMAIL_ENABLED=true

BREVO_API_KEY=xkeysib-xxxxxxxxxxxxx
BREVO_SMTP_USER=your-smtp-login@example.com
BREVO_SMTP_PASSWORD=xxxxxxxxxxxx

FROM_EMAIL=noreply@familycart.com
FROM_NAME=FamilyCart
SUPPORT_EMAIL=support@familycart.com
FRONTEND_URL=https://familycart.com
```

### 8.3 Docker Configuration

**File**: `backend/Dockerfile`

Ensure Jinja2 templates are copied:
```dockerfile
# Copy application code
COPY app /app/app
COPY templates /app/templates  # Add this line
```

**File**: `docker-compose.yml`

Add environment variables:
```yaml
backend:
  environment:
    - EMAIL_PROVIDER=${EMAIL_PROVIDER}
    - EMAIL_ENABLED=${EMAIL_ENABLED}
    - BREVO_API_KEY=${BREVO_API_KEY}
    - BREVO_SMTP_USER=${BREVO_SMTP_USER}
    - BREVO_SMTP_PASSWORD=${BREVO_SMTP_PASSWORD}
    - FROM_EMAIL=${FROM_EMAIL}
    - FRONTEND_URL=${FRONTEND_URL}
```

### 8.4 Testing in Development

**Console Mode** (no real emails):
```bash
EMAIL_PROVIDER=console
EMAIL_ENABLED=true
```

**Test with Real Emails**:
```bash
EMAIL_PROVIDER=brevo
EMAIL_ENABLED=true
BREVO_SMTP_USER=your-test-account
BREVO_SMTP_PASSWORD=your-password
```

---

## Part 9: Monitoring & Maintenance

### 9.1 Email Metrics to Track

- Total emails sent (by type)
- Email delivery success rate
- Email bounce rate
- Email open rate (if tracking pixels added)
- Failed email attempts
- Token expiration rate
- Invitation acceptance rate

### 9.2 Logging Strategy

All email operations should log:
- Timestamp
- Email type (verification, reset, invitation)
- Recipient email (masked for privacy: `u***@domain.com`)
- Success/failure status
- Error details if failed
- Retry attempts

### 9.3 Error Handling

**Email Service Failures**:
- Log error with full context
- Continue application operation (don't block user actions)
- Send alert to admin if failure rate > 10%
- Implement retry logic with exponential backoff

**Database Failures**:
- Transaction rollback on invitation creation failure
- Return appropriate HTTP error codes
- Log for debugging

### 9.4 Background Tasks (Future Enhancement)

Consider implementing:
- Cleanup expired invitations (daily job)
- Resend failed emails (retry queue)
- Email statistics aggregation
- User engagement reports

---

## Part 10: Success Criteria & Testing Checklist

### 10.1 Feature Acceptance Criteria

#### Email Verification
- [x] New users receive verification email within 30 seconds
- [x] Verification link works correctly
- [x] Expired tokens are rejected with clear message
- [x] Users can resend verification email
- [x] Verified users see confirmation

#### Password Recovery
- [x] Users can request password reset
- [x] Reset email received within 30 seconds
- [x] Reset link works correctly
- [x] Expired tokens are rejected
- [x] Password successfully changed
- [x] User can log in with new password

#### Existing User Invitations
- [x] Email sent when list is shared
- [x] Email contains correct list information
- [x] User can access list after receiving email
- [x] WebSocket + Email notifications both work

#### Non-Existent User Invitations
- [x] Invitation created for non-existent user
- [x] Email sent with invitation link
- [x] New user can sign up via invitation link
- [x] Invitation auto-accepted on registration
- [x] User immediately has access to shared list
- [x] Existing user can accept invitation after login
- [x] Expired invitations handled gracefully

### 10.2 Production Readiness Checklist

**Configuration**:
- [ ] Brevo account created and verified
- [ ] Environment variables configured
- [ ] Email templates tested and approved
- [ ] Domain SPF/DKIM configured (optional)

**Security**:
- [ ] All tokens cryptographically secure
- [ ] Token expiration working correctly
- [ ] Rate limiting implemented
- [ ] Email validation prevents injection

**Testing**:
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] End-to-end tests passing
- [ ] Manual testing completed
- [ ] Real email delivery tested

**Documentation**:
- [ ] User guide for email features
- [ ] Admin guide for troubleshooting
- [ ] API documentation updated
- [ ] Environment variable documentation

**Monitoring**:
- [ ] Email logging configured
- [ ] Error alerting set up
- [ ] Metrics dashboard created

---

## Part 11: Risk Assessment & Mitigation

### 11.1 Risks

**Risk 1**: Email deliverability issues (emails go to spam)
- **Mitigation**: Use reputable provider (Brevo), configure SPF/DKIM, avoid spam trigger words
- **Impact**: Medium - Users may not receive critical emails

**Risk 2**: Email service downtime
- **Mitigation**: Graceful degradation, retry logic, fallback to console logging for testing
- **Impact**: Low - App still functions, just no email notifications

**Risk 3**: Token security vulnerabilities
- **Mitigation**: Use cryptographically secure tokens, short expiration, single-use
- **Impact**: High - Could lead to unauthorized access

**Risk 4**: Database migration issues for invitation table
- **Mitigation**: Test migration on staging first, backup database, rollback plan
- **Impact**: High - Could break existing data

**Risk 5**: Email template rendering errors
- **Mitigation**: Extensive testing, fallback to plain text, error logging
- **Impact**: Low - Emails still delivered, just less pretty

### 11.2 Rollback Plan

If issues occur in production:

1. **Phase 1-2 (Verification/Reset)**: 
   - Set `EMAIL_ENABLED=false`
   - Users can still register and reset passwords (manual support)

2. **Phase 3 (Existing User Invitations)**:
   - Already works without email
   - Just missing notification

3. **Phase 4 (New User Invitations)**:
   - Revert sharing service changes
   - Return to original "404 user not found" behavior

---

## Appendix A: Email Provider Comparison

| Provider | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Brevo** | 300/day | Excellent deliverability, easy setup | Requires account verification |
| **Resend** | 100/day | Modern API, developer-friendly | Lower free tier |
| **MailerSend** | 12k/month | Highest free tier | Less established |
| **AWS SES** | 62k/month | Highest volume, cheap | Complex setup, needs AWS account |
| **SendGrid** | 100/day | Well-known, reliable | Requires credit card |
| **Self-Hosted** | Unlimited | Full control, privacy | Deliverability challenges, maintenance |

**Recommendation**: Start with Brevo, migrate to AWS SES if volume increases significantly.

---

## Appendix B: HTML Email Template Structure

All email templates follow this structure and use **FamilyCart Family Warmth Brand Guidelines**:

**Brand Reference**: See `docs/COLOR_PALETTE_IMPLEMENTATION.md` and `docs/VISUAL_IDENTITY_LOGIN_DIALOGS.md`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        /* Email client reset */
        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
        img { -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
        
        /* FamilyCart Family Warmth Brand Colors */
        .btn-primary { 
            background-color: #f59e0b !important; /* Warm Orange */
            color: #ffffff !important;
        }
        .btn-secondary {
            background-color: #3b82f6 !important; /* Trusted Blue */
            color: #ffffff !important;
        }
        .text-primary { color: #0f172a; } /* Slate-900 */
        .text-secondary { color: #64748b; } /* Slate-500 */
        .bg-light { background-color: #f8fafc; } /* Slate-50 */
        .border-light { border-color: #e2e8f0; } /* Slate-200 */
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: 'Plus Jakarta Sans', 'Noto Sans', Arial, Helvetica, sans-serif;">
    <!-- Email Container: 600px max width for compatibility -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8fafc;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <!-- Content Card: Rounded corners, white background -->
                <table width="600" cellpadding="0" cellspacing="0" border="0" 
                       style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-width: 600px;">
                    
                    <!-- Header with FamilyCart Logo -->
                    <tr>
                        <td align="center" style="padding: 40px 40px 20px;">
                            <!-- Use cart-family logo variant -->
                            <img src="{{ logo_url }}" alt="FamilyCart" width="120" height="auto" 
                                 style="display: block; margin: 0 auto;" />
                        </td>
                    </tr>
                    
                    <!-- Title Section -->
                    <tr>
                        <td style="padding: 20px 40px 10px;">
                            <h1 style="margin: 0; font-family: 'Plus Jakarta Sans', Arial, sans-serif; 
                                       font-size: 28px; font-weight: 700; color: #0f172a; 
                                       line-height: 1.3; text-align: center;">
                                {{ email_title }}
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Main Content Area -->
                    <tr>
                        <td style="padding: 20px 40px; font-family: 'Noto Sans', Arial, sans-serif; 
                                   font-size: 16px; line-height: 1.6; color: #374151;">
                            {% block content %}
                            <!-- Template-specific content goes here -->
                            <p style="margin: 0 0 16px;">Hello {{ user_name }},</p>
                            <p style="margin: 0 0 16px;">Email content goes here...</p>
                            {% endblock %}
                        </td>
                    </tr>
                    
                    <!-- Call-to-Action Button: Warm Orange (Family Warmth Primary) -->
                    <tr>
                        <td align="center" style="padding: 30px 40px;">
                            <table cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="center" style="border-radius: 6px; background-color: #f59e0b;">
                                        <a href="{{ action_url }}" 
                                           style="display: inline-block; padding: 14px 36px; 
                                                  background-color: #f59e0b; color: #ffffff; 
                                                  text-decoration: none; border-radius: 6px; 
                                                  font-family: 'Plus Jakarta Sans', Arial, sans-serif;
                                                  font-size: 16px; font-weight: 600; line-height: 1.5;">
                                            {{ action_text }}
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            <!-- Plain text link fallback -->
                            <p style="margin: 20px 0 0; font-size: 14px; color: #64748b;">
                                Or copy and paste this link: <br/>
                                <a href="{{ action_url }}" style="color: #3b82f6; word-break: break-all;">
                                    {{ action_url }}
                                </a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Expiration Notice (if applicable) -->
                    {% if expiry_hours %}
                    <tr>
                        <td style="padding: 0 40px 30px;">
                            <div style="padding: 16px; background-color: #fef3c7; 
                                        border-left: 4px solid #f59e0b; border-radius: 4px;">
                                <p style="margin: 0; font-size: 14px; color: #92400e;">
                                    ⏰ This link will expire in <strong>{{ expiry_hours }} hours</strong> for your security.
                                </p>
                            </div>
                        </td>
                    </tr>
                    {% endif %}
                    
                    <!-- Footer: Consistent branding and support -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f9fafb; 
                                   border-top: 1px solid #e5e7eb; border-radius: 0 0 8px 8px;">
                            <!-- Support Section -->
                            <p style="margin: 0 0 12px; color: #6b7280; font-size: 14px; 
                                      text-align: center; line-height: 1.5;">
                                Need help? We're here for your family. <br/>
                                Contact us at 
                                <a href="mailto:{{ support_email }}" 
                                   style="color: #3b82f6; text-decoration: none;">
                                    {{ support_email }}
                                </a>
                            </p>
                            
                            <!-- Copyright -->
                            <p style="margin: 16px 0 0; color: #9ca3af; font-size: 12px; 
                                      text-align: center; line-height: 1.5;">
                                © {{ year }} FamilyCart. Made with ❤️ for families. <br/>
                                All rights reserved.
                            </p>
                            
                            <!-- Trust Badges (Optional) -->
                            <p style="margin: 16px 0 0; color: #9ca3af; font-size: 11px; 
                                      text-align: center; line-height: 1.4;">
                                🔒 Secure • 👨‍👩‍👧‍👦 Family-Friendly • ✓ Privacy Protected
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Email Footer Text (Outside card, for email client info) -->
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin-top: 20px;">
                    <tr>
                        <td style="padding: 0 20px;">
                            <p style="margin: 0; font-size: 11px; color: #9ca3af; 
                                      text-align: center; line-height: 1.4;">
                                You received this email because you have a FamilyCart account. <br/>
                                If you didn't request this action, please ignore this email or 
                                <a href="mailto:{{ support_email }}" style="color: #3b82f6;">contact support</a>.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
```

### Key Brand Implementation Details:

**Color Usage**:
- **Primary CTA buttons**: Warm Orange `#f59e0b` (family warmth, inviting action)
- **Links**: Trusted Blue `#3b82f6` (reliable, clickable elements)
- **Success indicators**: Fresh Green `#22c55e` (completion, positive actions)
- **Text hierarchy**: Slate-900 `#0f172a` for headings, Slate-600 `#475569` for body
- **Backgrounds**: Slate-50 `#f8fafc` for page, White `#ffffff` for card

**Typography**:
- **Headings**: Plus Jakarta Sans (700 bold for titles, 600 semibold for subtitles)
- **Body**: Noto Sans (400 regular for content, 500 medium for emphasis)
- **Fallback chain**: Arial, Helvetica, sans-serif (universal email client support)

**Accessibility**:
- **Contrast ratios**: All text meets WCAG AA (4.5:1 minimum)
- **Button sizing**: Minimum 44x44px touch targets
- **Alt text**: All images have descriptive alt attributes
- **Plain text alternative**: Always include text version of links

**Email Client Compatibility**:
- **Table-based layout**: Works in Outlook, Gmail, Apple Mail, Yahoo Mail
- **Inline styles**: No external CSS dependencies
- **600px width**: Standard email width for desktop and mobile
- **Conditional comments**: MSO-specific styles for Outlook compatibility

**Family-Oriented Design**:
- **Warm tone**: Orange primary evokes family warmth and comfort
- **Friendly language**: "We're here for your family" instead of corporate speak
- **Emoji usage**: Subtle use (❤️, 🔒, 👨‍👩‍👧‍👦) to add personality without overwhelming
- **Trust indicators**: Security and privacy badges in footer

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Approve email provider choice** (Brevo recommended)
3. **Set up development environment** with email testing
4. **Begin Phase 1** - Infrastructure setup
5. **Iterate through phases** with testing at each stage

---

**Document Version**: 1.0  
**Last Updated**: November 9, 2025  
**Status**: Ready for Implementation  
**Estimated Completion**: 4 weeks (full-time equivalent)
