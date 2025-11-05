"""Test script for Milestone 4: Langfuse Integration."""
import asyncio
import os
import sys

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.llm_service import LLMService


async def test_langfuse_configured():
    """Test that Langfuse is configured."""
    print("Testing Langfuse configuration...")
    
    langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not langfuse_public_key or not langfuse_secret_key:
        print("✗ Langfuse keys not set in environment")
        print("  Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")
        print("  Get keys from: https://cloud.langfuse.com")
        return False
    
    print("✓ Langfuse keys found in environment")
    print(f"  Public key: {langfuse_public_key[:10]}...")
    print(f"  Host: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")
    return True


async def test_llm_with_tracing():
    """Test LLM call with Langfuse tracing."""
    print("Testing LLM with Langfuse tracing...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set")
        return False
    
    try:
        service = LLMService(api_key=api_key)
        
        if not service.langfuse_enabled:
            print("⚠ Langfuse not enabled - check configuration")
            return False
        
        response = await service.generate_response(
            messages=[
                {"role": "user", "content": "Say 'Langfuse test successful' and nothing else."}
            ],
            trace_name="test_langfuse_tracing"
        )
        
        if response and len(response) > 0:
            print(f"✓ LLM call with tracing successful")
            print(f"  Response: {response}")
            print("  → Check Langfuse dashboard for trace:")
            print("     https://cloud.langfuse.com")
            return True
        else:
            print("✗ Empty response from LLM")
            return False
    
    except Exception as e:
        print(f"✗ Error in traced LLM call: {e}")
        return False


async def test_multiple_traces():
    """Test multiple LLM calls with different trace names."""
    print("Testing multiple traces...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not set")
        return False
    
    try:
        service = LLMService(api_key=api_key)
        
        # First call
        await service.generate_response(
            messages=[{"role": "user", "content": "Count to 3"}],
            trace_name="test_trace_1"
        )
        
        # Second call
        await service.generate_response(
            messages=[{"role": "user", "content": "Say hello"}],
            trace_name="test_trace_2"
        )
        
        print("✓ Multiple traces created successfully")
        print("  → Check Langfuse dashboard for 2 traces:")
        print("     - test_trace_1")
        print("     - test_trace_2")
        return True
    
    except Exception as e:
        print(f"✗ Error creating multiple traces: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Milestone 4: Langfuse Integration - Tests")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("  1. Set OPENROUTER_API_KEY environment variable")
    print("  2. Set LANGFUSE_PUBLIC_KEY environment variable")
    print("  3. Set LANGFUSE_SECRET_KEY environment variable")
    print("  4. Have Langfuse account at https://cloud.langfuse.com")
    print()
    
    # Check for required keys
    missing_keys = []
    if not os.getenv("OPENROUTER_API_KEY"):
        missing_keys.append("OPENROUTER_API_KEY")
    if not os.getenv("LANGFUSE_PUBLIC_KEY"):
        missing_keys.append("LANGFUSE_PUBLIC_KEY")
    if not os.getenv("LANGFUSE_SECRET_KEY"):
        missing_keys.append("LANGFUSE_SECRET_KEY")
    
    if missing_keys:
        print(f"⚠ Missing environment variables: {', '.join(missing_keys)}")
        print()
        print("To set them:")
        print("  Windows PowerShell:")
        for key in missing_keys:
            print(f"    $env:{key}='your_value'")
        print()
        return
    
    tests_passed = 0
    tests_total = 3
    
    if await test_langfuse_configured():
        tests_passed += 1
    print()
    
    if await test_llm_with_tracing():
        tests_passed += 1
    print()
    
    if await test_multiple_traces():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"Tests: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("✓ Milestone 4 complete!")
        print()
        print("→ Go to Langfuse dashboard to verify traces:")
        print("  https://cloud.langfuse.com")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

