#!/usr/bin/env python3
"""
Simple test to check providers.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

try:
    from app.services.fallback_ai_service import fallback_ai_service
    print("✓ Successfully imported fallback_ai_service")
    
    # Test provider info
    info = fallback_ai_service.get_provider_info()
    print(f"Provider info: {info}")
    
    print(f"Primary provider type: {type(fallback_ai_service.primary_provider)}")
    print(f"Fallback provider type: {type(fallback_ai_service.fallback_provider)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
