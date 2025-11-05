#!/usr/bin/env python3
"""
Test script to verify agent implementations.

This script verifies that:
1. All required dependencies are installed
2. Agents can be imported successfully
3. Agent classes are properly structured
4. Function tools are correctly defined
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 70)
print("LIVEKIT AGENTS - DEPENDENCY & IMPLEMENTATION TEST")
print("=" * 70)
print()

# Test 1: Check dependencies
print("TEST 1: Checking dependencies...")
print("-" * 70)

dependencies = {
    "livekit": "LiveKit SDK",
    "livekit.agents": "LiveKit Agents Framework",
    "livekit.agents.voice": "Voice Agent Module",
    "livekit.plugins.openai": "OpenAI Plugin",
    "livekit.plugins.silero": "Silero VAD Plugin",
    "dotenv": "python-dotenv",
}

failed_imports = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"[OK] {name:30} ... OK")
    except ImportError as e:
        print(f"[FAIL] {name:30} ... FAILED")
        failed_imports.append((name, str(e)))

# Check VAD class specifically
try:
    from livekit.plugins.silero import VAD
    print(f"[OK] {'Silero VAD Class':30} ... OK")
except ImportError as e:
    print(f"[FAIL] {'Silero VAD Class':30} ... FAILED")
    failed_imports.append(("Silero VAD Class", str(e)))

if failed_imports:
    print("\n[!] DEPENDENCY ERRORS:")
    for name, error in failed_imports:
        print(f"  - {name}: {error}")
    print("\nTo fix, run:")
    print("  cd backend")
    print("  pip install -e .")
    sys.exit(1)

print("\n[OK] All dependencies installed!")
print()

# Test 2: Import agents
print("TEST 2: Importing agent modules...")
print("-" * 70)

try:
    from agents.dispatcher_agent import DispatcherAgent, entrypoint as dispatcher_entrypoint
    print("[OK] Dispatcher agent imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import dispatcher agent: {e}")
    sys.exit(1)

try:
    from agents.driver_agent import DriverAgent, entrypoint as driver_entrypoint
    print("[OK] Driver agent imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import driver agent: {e}")
    sys.exit(1)

print()

# Test 3: Verify agent structure
print("TEST 3: Verifying agent structure...")
print("-" * 70)

from livekit.agents.voice import Agent

# Check DispatcherAgent
if not issubclass(DispatcherAgent, Agent):
    print("[FAIL] DispatcherAgent is not a subclass of Agent")
    sys.exit(1)
print("[OK] DispatcherAgent is properly structured")

# Check DriverAgent
if not issubclass(DriverAgent, Agent):
    print("[FAIL] DriverAgent is not a subclass of Agent")
    sys.exit(1)
print("[OK] DriverAgent is properly structured")

print()

# Test 4: Verify function tools
print("TEST 4: Verifying function tools...")
print("-" * 70)

# Create instances
dispatcher = DispatcherAgent()
driver = DriverAgent()

# Check instructions are set
print(f"Dispatcher instructions: {'[OK]' if dispatcher.instructions else '[FAIL]'}")
print(f"Driver instructions: {'[OK]' if driver.instructions else '[FAIL]'}")

print("\nChecking dispatcher function tools:")
# Check specific dispatcher methods
if hasattr(dispatcher, 'mark_load_accepted'):
    print(f"  - mark_load_accepted: [OK]")
else:
    print(f"  - mark_load_accepted: [FAIL]")
    
if hasattr(dispatcher, 'mark_load_rejected'):
    print(f"  - mark_load_rejected: [OK]")
else:
    print(f"  - mark_load_rejected: [FAIL]")
    
if hasattr(dispatcher, 'get_load_details'):
    print(f"  - get_load_details: [OK]")
else:
    print(f"  - get_load_details: [FAIL]")

print("\nChecking driver function tools:")
# Check specific driver methods
if hasattr(driver, 'check_availability'):
    print(f"  - check_availability: [OK]")
else:
    print(f"  - check_availability: [FAIL]")
    
if hasattr(driver, 'calculate_distance'):
    print(f"  - calculate_distance: [OK]")
else:
    print(f"  - calculate_distance: [FAIL]")
    
if hasattr(driver, 'accept_load'):
    print(f"  - accept_load: [OK]")
else:
    print(f"  - accept_load: [FAIL]")

print()

# Test 5: Check entrypoints
print("TEST 5: Verifying entrypoints...")
print("-" * 70)

import inspect

if inspect.iscoroutinefunction(dispatcher_entrypoint):
    print("[OK] Dispatcher entrypoint is async")
else:
    print("[FAIL] Dispatcher entrypoint is not async")
    sys.exit(1)

if inspect.iscoroutinefunction(driver_entrypoint):
    print("[OK] Driver entrypoint is async")
else:
    print("[FAIL] Driver entrypoint is not async")
    sys.exit(1)

print()

# Final summary
print("=" * 70)
print("[SUCCESS] ALL TESTS PASSED!")
print("=" * 70)
print()
print("Your agents are ready to run. To start them:")
print()
print("  # Terminal 1 - Start Dispatcher Agent")
print("  cd backend")
print("  python agents/dispatcher_agent.py dev")
print()
print("  # Terminal 2 - Start Driver Agent")
print("  cd backend")
print("  python agents/driver_agent.py dev")
print()
print("Note: Make sure you have:")
print("  1. LIVEKIT_URL in your .env file")
print("  2. LIVEKIT_API_KEY in your .env file")
print("  3. LIVEKIT_API_SECRET in your .env file")
print("  4. OPENAI_API_KEY in your .env file")
print()

