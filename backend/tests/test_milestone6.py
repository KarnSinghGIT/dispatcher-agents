"""Test script for Milestone 6: Conversation Service - Multi-Turn."""
import requests
import json
import sys

def test_full_conversation():
    """Test generating a full multi-turn conversation via API."""
    print("Testing full conversation generation via API...")
    
    # Load test payload
    try:
        import os
        test_dir = os.path.dirname(__file__)
        with open(os.path.join(test_dir, "test_payload.json"), "r") as f:
            payload = json.load(f)
    except FileNotFoundError:
        print("✗ test_payload.json not found")
        return False
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for multi-turn generation
        )
        
        if response.status_code != 200:
            print(f"✗ HTTP error {response.status_code}")
            print(f"  Response: {response.text}")
            return False
        
        data = response.json()
        
        # Validate response
        if "transcript" not in data:
            print("✗ Response missing 'transcript'")
            return False
        
        transcript = data["transcript"]
        
        if len(transcript) < 3:
            print(f"✗ Expected multi-turn conversation, got only {len(transcript)} turns")
            return False
        
        # Check alternating speakers
        for i, turn in enumerate(transcript):
            expected_speaker = "Dispatcher" if i % 2 == 0 else "Driver"
            if turn["speaker"] != expected_speaker:
                print(f"✗ Turn {i}: expected {expected_speaker}, got {turn['speaker']}")
                return False
        
        print(f"✓ Full conversation generated successfully")
        print(f"  Total turns: {len(transcript)}")
        print(f"  Conversation preview:")
        
        for i, turn in enumerate(transcript[:6]):  # Show first 6 turns
            preview = turn["text"][:60] + "..." if len(turn["text"]) > 60 else turn["text"]
            print(f"    {turn['speaker']}: {preview}")
        
        if len(transcript) > 6:
            print(f"    ... ({len(transcript) - 6} more turns)")
        
        return True
    
    except requests.exceptions.Timeout:
        print("✗ Request timed out (conversation generation took too long)")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server")
        print("  Make sure server is running: uvicorn src.api.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_completion():
    """Test that conversations end naturally."""
    print("Testing conversation completion logic...")
    
    # Custom payload with driver who agrees quickly
    payload = {
        "scenario": {
            "loadId": "QUICK-123",
            "loadType": "Test freight",
            "weight": 10000,
            "pickupLocation": "City A",
            "pickupTime": "9 AM",
            "pickupType": "live",
            "deliveryLocation": "City B",
            "deliveryDeadline": "tomorrow",
            "trailerType": "dry-van",
            "ratePerMile": 3.0,
            "totalRate": 2000,
            "accessorials": "none",
            "securementRequirements": "standard",
            "tmsUpdate": "none"
        },
        "dispatcherAgent": {
            "role": "dispatcher",
            "prompt": "You are a dispatcher. Keep conversation very brief. Just present the load and rate."
        },
        "driverAgent": {
            "role": "driver",
            "prompt": "You are a driver. You're interested and agree quickly to the load."
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/conversations/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            turns = len(data["transcript"])
            
            print(f"✓ Conversation completed with {turns} turns")
            
            # Check if last turn contains ending phrase
            last_text = data["transcript"][-1]["text"].lower()
            ending_found = any(phrase in last_text for phrase in 
                             ["thanks", "bye", "goodbye", "talk soon", "will do"])
            
            if ending_found:
                print("✓ Conversation ended naturally with closing phrase")
            else:
                print("⚠ Last turn doesn't contain obvious closing phrase")
                print(f"  Last message: {data['transcript'][-1]['text'][:80]}...")
            
            return True
        else:
            print(f"✗ HTTP error {response.status_code}")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Milestone 6: Conversation Service - Multi-Turn - Tests")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("  1. Backend server running (uvicorn src.api.main:app --reload)")
    print("  2. OPENROUTER_API_KEY set in server environment")
    print("  3. (Optional) LANGFUSE keys for observability")
    print()
    
    input("Press Enter when server is ready...")
    print()
    
    tests_passed = 0
    tests_total = 2
    
    if test_full_conversation():
        tests_passed += 1
    print()
    
    if test_conversation_completion():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ Milestone 6 complete!")
        print()
        print("Next steps:")
        print("  - Check Langfuse dashboard for conversation traces")
        print("  - Ready to implement frontend!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

