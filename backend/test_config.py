#!/usr/bin/env python3
"""
Simple configuration test
"""
import os
import sys

sys.path.append("/home/honzik/GitHub/FamilyCart/FamilyCart/backend")

# Test environment variables directly
print("Environment variables:")
print(f"  AI_PROVIDER: {os.getenv('AI_PROVIDER', 'not set')}")
print(f"  OLLAMA_MODEL_NAME: {os.getenv('OLLAMA_MODEL_NAME', 'not set')}")
print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'not set')}")

# Test Pydantic settings
try:
    from app.core.config import settings

    print("\nPydantic Settings:")
    print(f"  AI_PROVIDER: {settings.AI_PROVIDER}")
    print(f"  OLLAMA_MODEL_NAME: {settings.OLLAMA_MODEL_NAME}")
    print(f"  OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
    print(f"  GEMINI_MODEL_NAME: {settings.GEMINI_MODEL_NAME}")
except Exception as e:
    print(f"Error loading settings: {e}")
