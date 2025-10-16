#!/usr/bin/env python3
"""
Test script to verify CI/CD runner stability.
This script will be picked up by the test suite and help verify
that runners can handle various operations without crashing.
"""

import time
import sys
import subprocess
import os


def test_runner_stability():
    """Test that runners can handle various operations."""
    print("Testing runner stability...")
    
    # Test 1: Basic computation
    result = sum(range(1000))
    assert result == 499500, f"Expected 499500, got {result}"
    print("✓ Basic computation test passed")
    
    # Test 2: File operations
    test_file = "/tmp/runner_test.txt"
    with open(test_file, "w") as f:
        f.write("Runner stability test\n")
    
    with open(test_file, "r") as f:
        content = f.read().strip()
    
    assert content == "Runner stability test", f"File content mismatch: {content}"
    os.remove(test_file)
    print("✓ File operations test passed")
    
    # Test 3: Network connectivity (check if docker is accessible)
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Docker connectivity test passed")
        else:
            print("⚠ Docker not accessible (expected in some environments)")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠ Docker command timeout or not found")
    
    # Test 4: Memory allocation
    test_data = [i for i in range(10000)]
    assert len(test_data) == 10000, f"Memory test failed: {len(test_data)}"
    del test_data
    print("✓ Memory allocation test passed")
    
    print("All runner stability tests completed successfully!")
    return True


if __name__ == "__main__":
    try:
        test_runner_stability()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Runner stability test failed: {e}")
        sys.exit(1)