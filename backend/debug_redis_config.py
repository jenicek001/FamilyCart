#!/usr/bin/env python3
"""
Debug script to check Redis configuration loading
"""
import os

from app.core.config import settings

print("=== Debug Redis Configuration ===")
print(f"REDIS_HOST: {settings.REDIS_HOST}")
print(f"REDIS_PORT: {settings.REDIS_PORT}")
print(f"REDIS_PASSWORD: {repr(settings.REDIS_PASSWORD)}")
print(f"REDIS_URL: {repr(settings.REDIS_URL)}")

# Check environment variables directly
print("\n=== Environment Variables ===")
print(f"REDIS_PASSWORD (env): {repr(os.getenv('REDIS_PASSWORD'))}")
print(f"REDIS_HOST (env): {repr(os.getenv('REDIS_HOST'))}")
print(f"REDIS_PORT (env): {repr(os.getenv('REDIS_PORT'))}")

# Check if .env file exists
print(f"\n=== File System ===")
print(f".env file exists: {os.path.exists('.env')}")
if os.path.exists(".env"):
    with open(".env", "r") as f:
        content = f.read()
        print("REDIS lines in .env:")
        for line in content.split("\n"):
            if "REDIS" in line:
                print(f"  {line}")
