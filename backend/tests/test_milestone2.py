"""Test script for Milestone 2: Pydantic Models & API Structure."""
import requests
import json
import sys

def test_conversation_endpoint():
    """Test the conversation generation endpoint."""
    print("Testing conversation endpoint...")
    
    # Load test payload
    import os
    test_dir = os.path.dirname(__file__)
    with open(os.path.join(test_dir, "test_payload.json"), "r") as f:
        payload = json.load(f)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "conversationId" not in data:
                print("✗ Response missing 'conversationId'")
                return False
            
            if "transcript" not in data:
                print("✗ Response missing 'transcript'")
                return False
            
            if not isinstance(data["transcript"], list):
                print("✗ 'transcript' is not a list")
                return False
            
            if len(data["transcript"]) == 0:
                print("✗ 'transcript' is empty")
                return False
            
            # Validate first turn
            first_turn = data["transcript"][0]
            if "speaker" not in first_turn or "text" not in first_turn or "timestamp" not in first_turn:
                print("✗ Conversation turn missing required fields")
                return False
            
            print("✓ Conversation endpoint working correctly")
            print(f"  - Conversation ID: {data['conversationId']}")
            print(f"  - Turns: {len(data['transcript'])}")
            print(f"  - First speaker: {first_turn['speaker']}")
            print(f"  - First message: {first_turn['text'][:50]}...")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure it's running.")
        print("  Run: uvicorn src.api.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Error testing conversation endpoint: {e}")
        return False

def test_api_docs():
    """Test that API documentation is available."""
    print("Testing API documentation...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✓ API documentation available at /docs")
            return True
        else:
            print(f"✗ API docs returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error accessing API docs: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Milestone 2: Pydantic Models & API Structure - Tests")
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
    
    if test_conversation_endpoint():
        tests_passed += 1
    print()
    
    if test_api_docs():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ Milestone 2 complete!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

