"""Test script for Milestone 5: Conversation Service - Single Turn."""
import asyncio
import os
import sys
import json

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.llm_service import LLMService
from services.conversation_service import ConversationService


async def test_single_turn():
    """Test generating a single-turn conversation."""
    print("Testing single-turn conversation generation...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set")
        return False
    
    try:
        # Load test scenario
        import os
        test_dir = os.path.dirname(__file__)
        with open(os.path.join(test_dir, "test_payload.json"), "r") as f:
            payload = json.load(f)
        
        # Initialize services
        llm_service = LLMService(api_key=api_key)
        conv_service = ConversationService(llm_service)
        
        # Generate conversation (single turn)
        conversation = await conv_service.generate_conversation(
            scenario=payload["scenario"],
            dispatcher_prompt=payload["dispatcherAgent"]["prompt"],
            driver_prompt=payload["driverAgent"]["prompt"],
            max_turns=1
        )
        
        if len(conversation) != 1:
            print(f"✗ Expected 1 turn, got {len(conversation)}")
            return False
        
        turn = conversation[0]
        
        if turn.speaker != "Dispatcher":
            print(f"✗ Expected speaker 'Dispatcher', got '{turn.speaker}'")
            return False
        
        if not turn.text or len(turn.text) < 5:
            print("✗ Dispatcher message too short or empty")
            return False
        
        print("✓ Single-turn conversation generated successfully")
        print(f"  Speaker: {turn.speaker}")
        print(f"  Message: {turn.text[:100]}...")
        print(f"  Timestamp: {turn.timestamp}")
        return True
    
    except Exception as e:
        print(f"✗ Error generating conversation: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scenario_formatting():
    """Test scenario formatting."""
    print("Testing scenario formatting...")
    
    try:
        with open("test_payload.json", "r") as f:
            payload = json.load(f)
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        llm_service = LLMService(api_key=api_key)
        conv_service = ConversationService(llm_service)
        
        formatted = conv_service._format_scenario(payload["scenario"])
        
        # Check that key elements are in formatted scenario
        required_elements = ["HDX-2478", "HVAC units", "42000", "Dallas TX", "Atlanta GA"]
        
        for element in required_elements:
            if element not in formatted:
                print(f"✗ Missing '{element}' in formatted scenario")
                return False
        
        print("✓ Scenario formatting correct")
        print(f"  Formatted scenario preview:")
        for line in formatted.strip().split('\n')[:3]:
            print(f"    {line}")
        return True
    
    except Exception as e:
        print(f"✗ Error testing scenario formatting: {e}")
        return False


async def test_with_custom_prompts():
    """Test with custom dispatcher prompts."""
    print("Testing with custom prompts...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set")
        return False
    
    try:
        # Simple test scenario
        scenario = {
            "loadId": "TEST-123",
            "loadType": "Test freight",
            "weight": 10000,
            "pickupLocation": "City A",
            "pickupTime": "9 AM",
            "pickupType": "live",
            "deliveryLocation": "City B",
            "deliveryDeadline": "next day",
            "trailerType": "dry-van",
            "ratePerMile": 2.0,
            "totalRate": 1000,
            "accessorials": "none",
            "securementRequirements": "standard",
            "tmsUpdate": "none"
        }
        
        llm_service = LLMService(api_key=api_key)
        conv_service = ConversationService(llm_service)
        
        conversation = await conv_service.generate_conversation(
            scenario=scenario,
            dispatcher_prompt="You are a friendly dispatcher named Sarah.",
            driver_prompt="You are a driver named Mike.",
            max_turns=1
        )
        
        if len(conversation) == 1 and conversation[0].speaker == "Dispatcher":
            print("✓ Custom prompts working")
            print(f"  Message: {conversation[0].text[:80]}...")
            return True
        else:
            print("✗ Custom prompts failed")
            return False
    
    except Exception as e:
        print(f"✗ Error with custom prompts: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Milestone 5: Conversation Service - Single Turn - Tests")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("  1. Set OPENROUTER_API_KEY environment variable")
    print("  2. (Optional) Set LANGFUSE keys for tracing")
    print("  3. Have test_payload.json in backend directory")
    print()
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠ OPENROUTER_API_KEY not found in environment")
        print()
        return
    
    tests_passed = 0
    tests_total = 3
    
    if await test_scenario_formatting():
        tests_passed += 1
    print()
    
    if await test_single_turn():
        tests_passed += 1
    print()
    
    if await test_with_custom_prompts():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ Milestone 5 complete!")
        if os.getenv("LANGFUSE_PUBLIC_KEY"):
            print("  → Check Langfuse dashboard for conversation traces")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

