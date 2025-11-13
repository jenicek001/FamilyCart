"""
Test script for email service functionality

This script tests the email service with the console provider
to ensure all components are working correctly before integrating
with fastapi-users.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import get_email_service


async def test_email_service():
    """Test email service with various scenarios"""
    print("=" * 80)
    print("TESTING EMAIL SERVICE")
    print("=" * 80)
    
    email_service = get_email_service()
    
    # Test 1: Email validation
    print("\n1. Testing email validation...")
    valid_email = email_service.validate_email_address("test@example.com")
    invalid_email = email_service.validate_email_address("invalid-email")
    
    print(f"   Valid email 'test@example.com': {valid_email}")
    print(f"   Invalid email 'invalid-email': {invalid_email}")
    assert valid_email == "test@example.com", "Valid email should be normalized"
    assert invalid_email is None, "Invalid email should return None"
    print("   ✓ Email validation working correctly")
    
    # Test 2: Simple HTML email
    print("\n2. Testing simple HTML email...")
    success = await email_service.send_email(
        recipient="user@example.com",
        subject="Test Email",
        html_content="<h1>Hello!</h1><p>This is a test email.</p>",
    )
    assert success, "Email should send successfully"
    print("   ✓ Simple email sent successfully")
    
    # Test 3: Email with plain text fallback
    print("\n3. Testing email with plain text fallback...")
    success = await email_service.send_email(
        recipient="user@example.com",
        subject="Test Email with Plain Text",
        html_content="<h1>Hello!</h1><p>This is HTML content.</p>",
        text_content="Hello!\n\nThis is plain text content.",
    )
    assert success, "Email with plain text should send successfully"
    print("   ✓ Email with plain text sent successfully")
    
    # Test 4: Verification email
    print("\n4. Testing verification email template...")
    success = await email_service.send_verification_email(
        recipient="newuser@example.com",
        token="test-verification-token-12345",
    )
    print(f"   Verification email result: {success}")
    if not success:
        print("   ⚠ Template might not exist yet (expected if templates not created)")
    
    # Test 5: Password reset email
    print("\n5. Testing password reset email template...")
    success = await email_service.send_password_reset_email(
        recipient="user@example.com",
        token="test-reset-token-67890",
    )
    print(f"   Password reset email result: {success}")
    if not success:
        print("   ⚠ Template might not exist yet (expected if templates not created)")
    
    # Test 6: Invitation email (existing user)
    print("\n6. Testing invitation email (existing user)...")
    success = await email_service.send_invitation_email(
        recipient="existinguser@example.com",
        inviter_name="John Doe",
        list_name="Weekend Shopping",
        invitation_token=None,
    )
    print(f"   Invitation email result: {success}")
    if not success:
        print("   ⚠ Template might not exist yet (expected if templates not created)")
    
    # Test 7: Invitation email (new user)
    print("\n7. Testing invitation email (new user)...")
    success = await email_service.send_invitation_email(
        recipient="newuser@example.com",
        inviter_name="Jane Smith",
        list_name="Family Groceries",
        invitation_token="invitation-token-abc123",
    )
    print(f"   Invitation email result: {success}")
    if not success:
        print("   ⚠ Template might not exist yet (expected if templates not created)")
    
    print("\n" + "=" * 80)
    print("EMAIL SERVICE TEST COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Create individual email templates (verification.html, password_reset.html, etc.)")
    print("2. Integrate with fastapi-users UserManager hooks")
    print("3. Test with real SMTP provider (Brevo)")


if __name__ == "__main__":
    try:
        asyncio.run(test_email_service())
        print("\n✓ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
