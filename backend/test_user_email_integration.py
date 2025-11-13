"""
Test email integration with UserManager hooks
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

from app.core.users import UserManager
from app.models.user import User


async def test_user_manager_hooks():
    """Test that UserManager hooks properly call email service"""
    print("=" * 80)
    print("TESTING USER MANAGER EMAIL INTEGRATION")
    print("=" * 80)
    
    # Mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = "test-user-id-123"
    mock_user.email = "test@example.com"
    
    # Mock user_db
    mock_user_db = AsyncMock()
    
    # Create UserManager instance
    user_manager = UserManager(mock_user_db)
    
    # Test 1: on_after_register
    print("\n1. Testing on_after_register hook...")
    print(f"   Registering user: {mock_user.email}")
    await user_manager.on_after_register(mock_user, None)
    print("   ✅ Hook executed without errors")
    
    # Test 2: on_after_forgot_password
    print("\n2. Testing on_after_forgot_password hook...")
    print(f"   Password reset requested for: {mock_user.email}")
    test_token = "test-reset-token-xyz789"
    
    with patch('app.core.users.get_email_service') as mock_get_email_service:
        mock_email_service = AsyncMock()
        mock_get_email_service.return_value = mock_email_service
        
        await user_manager.on_after_forgot_password(mock_user, test_token, None)
        
        # Verify email service was called
        mock_email_service.send_password_reset_email.assert_called_once_with(
            recipient=mock_user.email,
            token=test_token,
        )
        print("   ✅ Password reset email triggered correctly")
    
    # Test 3: on_after_request_verify
    print("\n3. Testing on_after_request_verify hook...")
    print(f"   Verification requested for: {mock_user.email}")
    test_verify_token = "test-verify-token-abc123"
    
    with patch('app.core.users.get_email_service') as mock_get_email_service:
        mock_email_service = AsyncMock()
        mock_get_email_service.return_value = mock_email_service
        
        await user_manager.on_after_request_verify(mock_user, test_verify_token, None)
        
        # Verify email service was called
        mock_email_service.send_verification_email.assert_called_once_with(
            recipient=mock_user.email,
            token=test_verify_token,
        )
        print("   ✅ Verification email triggered correctly")
    
    print("\n" + "=" * 80)
    print("✅ ALL USER MANAGER EMAIL INTEGRATION TESTS PASSED!")
    print("=" * 80)
    print("\nThe UserManager hooks are properly integrated with email service.")
    print("Emails will be sent automatically when:")
    print("  - User requests email verification")
    print("  - User requests password reset")


if __name__ == "__main__":
    try:
        asyncio.run(test_user_manager_hooks())
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
