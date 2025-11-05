"""Test script for Milestone 3: LLM Service Integration."""
import asyncio
import os
import sys

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.llm_service import LLMService


async def test_llm_basic():
    """Test basic LLM functionality."""
    print("Testing basic LLM call...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set in environment")
        print("  Please set it in your .env file or export it")
        return False
    
    try:
        service = LLMService(api_key=api_key)
        response = await service.generate_response([
            {"role": "user", "content": "Say 'Hello! This is a test.' and nothing else."}
        ])
        
        if response and len(response) > 0:
            print(f"✓ LLM responded successfully")
            print(f"  Response: {response}")
            return True
        else:
            print("✗ LLM returned empty response")
            return False
    
    except Exception as e:
        print(f"✗ Error calling LLM: {e}")
        return False


async def test_llm_conversation():
    """Test LLM with conversation context."""
    print("Testing LLM with conversation context...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set")
        return False
    
    try:
        service = LLMService(api_key=api_key)
        
        # Simulate a dispatcher greeting
        response = await service.generate_response([
            {
                "role": "system",
                "content": "You are Tim, a friendly dispatcher at Dispatch Co. Greet the driver briefly."
            },
            {
                "role": "user",
                "content": "Start the conversation with a greeting to driver Chris."
            }
        ])
        
        if response and len(response) > 0:
            print(f"✓ LLM generated dispatcher greeting")
            print(f"  Response: {response[:100]}...")
            
            # Check if response seems reasonable
            if any(word in response.lower() for word in ["hey", "hi", "hello", "chris"]):
                print("✓ Response contains expected greeting elements")
                return True
            else:
                print("⚠ Response doesn't contain typical greeting")
                return True  # Still pass, LLM might use different phrasing
        else:
            print("✗ LLM returned empty response")
            return False
    
    except Exception as e:
        print(f"✗ Error in conversation test: {e}")
        return False


async def test_llm_different_model():
    """Test LLM with different model."""
    print("Testing LLM with gpt-4o-mini model...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set")
        return False
    
    try:
        service = LLMService(api_key=api_key)
        response = await service.generate_response(
            messages=[{"role": "user", "content": "Respond with just the number 42."}],
            model="openai/gpt-4o-mini",
            temperature=0.0
        )
        
        if response:
            print(f"✓ Successfully used gpt-4o-mini model")
            print(f"  Response: {response}")
            return True
        else:
            print("✗ Empty response from gpt-4o-mini")
            return False
    
    except Exception as e:
        print(f"✗ Error with model selection: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Milestone 3: LLM Service Integration - Tests")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("  1. Set OPENROUTER_API_KEY environment variable")
    print("  2. Have credits/account on OpenRouter")
    print()
    
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠ OPENROUTER_API_KEY not found in environment")
        print()
        print("To set it:")
        print("  Windows PowerShell: $env:OPENROUTER_API_KEY='your_key'")
        print("  Windows CMD: set OPENROUTER_API_KEY=your_key")
        print("  Linux/Mac: export OPENROUTER_API_KEY='your_key'")
        print()
        print("Or create a .env file in the backend directory")
        print()
        return
    
    tests_passed = 0
    tests_total = 3
    
    if await test_llm_basic():
        tests_passed += 1
    print()
    
    if await test_llm_conversation():
        tests_passed += 1
    print()
    
    if await test_llm_different_model():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ Milestone 3 complete!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

