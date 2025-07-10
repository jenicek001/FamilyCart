#!/usr/bin/env python3
"""
Test script to verify the new Gemini 2.5 Flash Lite model configuration
"""
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.core.config import settings
    print("✅ Configuration loaded successfully")
    print(f"📋 Current Gemini model: {settings.GEMINI_MODEL_NAME}")
    print(f"🤖 AI Provider: {settings.AI_PROVIDER}")
    
    # Test if the provider can be initialized (if API key is available)
    if settings.GOOGLE_API_KEY:
        from app.services.ai_factory import AIProviderFactory
        try:
            provider = AIProviderFactory.get_provider()
            print(f"✅ AI Provider initialized: {provider.provider_name}")
            print(f"📱 Model name: {provider.model_name}")
        except Exception as e:
            print(f"⚠️  AI Provider initialization failed: {e}")
    else:
        print("⚠️  GOOGLE_API_KEY not set - provider initialization skipped")
        
    # Verify the model string
    expected_model = "gemini-2.5-flash-lite-preview-06-17"
    if settings.GEMINI_MODEL_NAME == expected_model:
        print(f"✅ Model configuration correct: {expected_model}")
    else:
        print(f"❌ Model configuration incorrect. Expected: {expected_model}, Got: {settings.GEMINI_MODEL_NAME}")
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("💡 Make sure you're running this from the backend directory with: poetry run python test_gemini_model_config.py")
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
