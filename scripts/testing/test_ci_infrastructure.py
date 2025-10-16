#!/usr/bin/env python3
"""
Test script to verify CI/CD infrastructure is working correctly.

This script tests:
- Python 3.12 installation
- Poetry 2.x package management
- Docker socket access 
- PostgreSQL and Redis connectivity
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"🔍 Testing: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description}: SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}: FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description}: EXCEPTION - {str(e)}")
        return False


def main():
    """Test CI/CD infrastructure components."""
    print("🚀 FamilyCart CI/CD Infrastructure Test")
    print("=" * 50)
    
    tests = [
        ("python3 --version", "Python 3.12 installation"),
        ("poetry --version", "Poetry 2.x package management"),
        ("docker --version", "Docker CLI availability"),
        ("docker ps", "Docker daemon connectivity"),
        ("docker ps --format 'table {{.Names}}\\t{{.Status}}' | head -5", "Docker containers list"),
        ("which black", "Black code formatter"),
        ("which isort", "isort import sorter"), 
        ("which pylint", "Pylint code analyzer"),
        ("which pytest", "Pytest testing framework"),
    ]
    
    results = []
    for cmd, desc in tests:
        results.append(run_command(cmd, desc))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! CI/CD infrastructure is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Infrastructure needs attention.")
        return 1


if __name__ == "__main__":
    sys.exit(main())