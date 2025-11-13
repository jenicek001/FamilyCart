"""
Test sending a real email through Brevo SMTP

This script sends a test email to verify Brevo configuration is working.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import get_email_service


async def test_brevo_email():
    """Send a real test email through Brevo"""
    print("=" * 80)
    print("TESTING BREVO EMAIL SERVICE")
    print("=" * 80)
    
    email_service = get_email_service()
    
    # Send to specified email
    recipient = "honzik.zahradnik@gmail.com"
    
    # Validate email
    validated = email_service.validate_email_address(recipient)
    if not validated:
        print(f"❌ Invalid email address: {recipient}")
        return False
    
    print(f"\n✓ Email validated: {validated}")
    print(f"\nSending test email to {validated}...")
    print("This may take a few seconds...")
    
    # Send test email
    success = await email_service.send_email(
        recipient=validated,
        subject="Test Email from FamilyCart",
        html_content="""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1 style="color: #f59e0b;">🛒 FamilyCart Test Email</h1>
                <p>Hello!</p>
                <p>This is a test email sent through Brevo SMTP to verify your email configuration is working correctly.</p>
                <p><strong>If you're reading this, it worked! 🎉</strong></p>
                <hr style="border: 1px solid #e5e5e5; margin: 20px 0;">
                <p style="color: #666; font-size: 14px;">
                    Sent from FamilyCart Backend<br>
                    Email Service Test
                </p>
            </body>
        </html>
        """,
        text_content="""
FamilyCart Test Email

Hello!

This is a test email sent through Brevo SMTP to verify your email configuration is working correctly.

If you're reading this, it worked! 🎉

---
Sent from FamilyCart Backend
Email Service Test
        """,
    )
    
    print("\n" + "=" * 80)
    if success:
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nCheck your inbox at {validated}")
        print("Note: Check spam folder if you don't see it in a few minutes")
        return True
    else:
        print("❌ EMAIL SENDING FAILED")
        print("=" * 80)
        print("\nCheck the error messages above for details")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(test_brevo_email())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
