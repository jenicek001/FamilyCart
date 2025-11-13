"""
Send all email templates to test email address via Brevo
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import get_email_service


async def test_all_templates():
    """Send all email templates to honzik.zahradnik@gmail.com"""
    print("=" * 80)
    print("TESTING ALL EMAIL TEMPLATES VIA BREVO")
    print("=" * 80)
    
    email_service = get_email_service()
    recipient = "honzik.zahradnik@gmail.com"
    
    print(f"\nSending all 4 email templates to {recipient}...\n")
    
    # 1. Verification email
    print("1. Sending verification email...")
    success = await email_service.send_verification_email(
        recipient=recipient,
        token="test-verification-token-abc123",
    )
    print(f"   {'✅ Sent' if success else '❌ Failed'}")
    
    # 2. Password reset email
    print("2. Sending password reset email...")
    success = await email_service.send_password_reset_email(
        recipient=recipient,
        token="test-reset-token-xyz789",
    )
    print(f"   {'✅ Sent' if success else '❌ Failed'}")
    
    # 3. Invitation for existing user
    print("3. Sending invitation (existing user)...")
    success = await email_service.send_invitation_email(
        recipient=recipient,
        inviter_name="John Doe",
        list_name="Weekend Shopping",
        list_id="abc123-list-id",  # Specific list for existing user
        invitation_token=None,  # Existing user
    )
    print(f"   {'✅ Sent' if success else '❌ Failed'}")
    
    # 4. Invitation for new user
    print("4. Sending invitation (new user)...")
    success = await email_service.send_invitation_email(
        recipient=recipient,
        inviter_name="Jane Smith",
        list_name="Family Groceries",
        list_id=None,  # No list_id for new users (goes to registration)
        invitation_token="invitation-token-new-user-456",
    )
    print(f"   {'✅ Sent' if success else '❌ Failed'}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TEMPLATES SENT!")
    print("=" * 80)
    print(f"\nCheck your inbox at {recipient}")
    print("You should receive 4 emails showcasing all templates with Family Warmth branding")


if __name__ == "__main__":
    try:
        asyncio.run(test_all_templates())
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
