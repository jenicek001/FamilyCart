#!/usr/bin/env python3
"""
Test script to verify UUID serialization fixes.
"""

import sys
import os
import json

sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

try:
    import uuid
    from datetime import datetime
    from app.schemas.item import ItemRead, UserBasic

    print("🔧 Testing UUID Serialization Fix")
    print("=" * 40)

    # Test UserBasic with UUID
    test_user = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "nickname": "Test User",
    }

    user_obj = UserBasic(**test_user)
    user_json = user_obj.model_dump(mode="json")
    print("✅ UserBasic serialization:", json.dumps(user_json))

    # Test ItemRead with UUID fields
    test_item_data = {
        "id": 1,
        "name": "Test Item",
        "shopping_list_id": 1,
        "owner_id": uuid.uuid4(),
        "last_modified_by_id": uuid.uuid4(),
        "is_completed": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    item_obj = ItemRead(**test_item_data)
    item_json = item_obj.model_dump(mode="json")
    print("✅ ItemRead serialization:", json.dumps(item_json))

    print("\n🎉 UUID serialization fix verified!")
    print("✅ UUIDs are now properly converted to strings")
    print("✅ WebSocket JSON serialization should work correctly")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
