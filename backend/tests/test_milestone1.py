"""Test script for Milestone 1: Backend Foundation Setup."""
import subprocess
import time
import requests
import sys

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200 and response.json() == {"status": "ok"}:
            print("✓ Health endpoint working correctly")
            return True
        else:
            print(f"✗ Health endpoint returned unexpected response: {response.json()}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure it's running.")
        print("  Run: uvicorn src.api.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Error testing health endpoint: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "version" in data:
                print(f"✓ Root endpoint working: {data['message']}")
                return True
        print(f"✗ Root endpoint returned unexpected response: {response.json()}")
        return False
    except Exception as e:
        print(f"✗ Error testing root endpoint: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Milestone 1: Backend Foundation Setup - Tests")
    print("=" * 60)
    print()
    print("Make sure the server is running:")
    print("  cd backend")
    print("  uvicorn src.api.main:app --reload")
    print()
    
    input("Press Enter when server is ready...")
    print()
    
    tests_passed = 0
    tests_total = 2
    
    if test_health_endpoint():
        tests_passed += 1
    print()
    
    if test_root_endpoint():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ Milestone 1 complete!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

