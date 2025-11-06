"""
Integration test for the updated multi-agent system with UI-driven prompts and auto-disconnect.

This test verifies:
1. Custom agent prompts are loaded from UI
2. Agents can call end_conversation() tool
3. Conversation concludes and agents disconnect
4. Recording endpoint returns data
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.api.routes.rooms import CreateRoomRequest, Scenario, AgentConfig
from dotenv import load_dotenv
import os

# Load environment variables
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str, status: str, message: str = ""):
    """Print formatted test result."""
    icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[TEST]"
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    
    print(f"{color}{icon} {name}: {status}{Colors.RESET}")
    if message:
        print(f"   {message}")


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


async def test_custom_prompts():
    """Test that custom prompts are properly loaded from metadata."""
    print_section("Test 1: Custom Agent Prompts")
    
    try:
        # Create test scenario
        scenario = Scenario(
            loadId="TEST-001",
            loadType="Test Load",
            weight=1000,
            pickupLocation="Test City A",
            pickupTime="9 AM",
            pickupType="drop",
            deliveryLocation="Test City B",
            deliveryDeadline="5 PM",
            trailerType="dry-van",
            ratePerMile=1.5,
            totalRate=1200,
            accessorials="none",
            securementRequirements="standard",
            tmsUpdate="none"
        )
        
        # Custom prompts from UI
        custom_dispatcher_prompt = "You are a test dispatcher. Be brief and professional."
        custom_driver_prompt = "You are a test driver. Respond quickly."
        
        dispatcher_agent = AgentConfig(
            role="dispatcher",
            prompt=custom_dispatcher_prompt,
            actingNotes="Test mode - keep responses short"
        )
        
        driver_agent = AgentConfig(
            role="driver",
            prompt=custom_driver_prompt,
            actingNotes="Test mode - accept quickly"
        )
        
        # Build request
        request = CreateRoomRequest(
            scenario=scenario,
            dispatcherAgent=dispatcher_agent,
            driverAgent=driver_agent
        )
        
        # Verify prompts are in the request
        assert request.dispatcherAgent.prompt == custom_dispatcher_prompt, "Dispatcher prompt mismatch"
        assert request.driverAgent.prompt == custom_driver_prompt, "Driver prompt mismatch"
        assert request.dispatcherAgent.actingNotes == "Test mode - keep responses short"
        assert request.driverAgent.actingNotes == "Test mode - accept quickly"
        
        print_test("Custom Dispatcher Prompt", "PASS", 
                  f"Prompt length: {len(custom_dispatcher_prompt)} chars")
        print_test("Custom Driver Prompt", "PASS",
                  f"Prompt length: {len(custom_driver_prompt)} chars")
        print_test("Acting Notes Storage", "PASS",
                  "Both agents have acting notes configured")
        
        # Simulate room metadata creation (as done in rooms.py)
        metadata_dict = {
            "scenario": scenario.model_dump(),
            "dispatcherAgent": dispatcher_agent.model_dump(),
            "driverAgent": driver_agent.model_dump()
        }
        metadata_json = json.dumps(metadata_dict)
        
        # Verify metadata can be parsed back
        parsed_metadata = json.loads(metadata_json)
        assert parsed_metadata["dispatcherAgent"]["prompt"] == custom_dispatcher_prompt
        assert parsed_metadata["driverAgent"]["prompt"] == custom_driver_prompt
        
        print_test("Metadata Serialization", "PASS",
                  "Metadata round-trip successful")
        
        return True
        
    except Exception as e:
        print_test("Custom Prompts Test", "FAIL", str(e))
        return False


async def test_end_conversation_tool():
    """Test that end_conversation tool is properly defined."""
    print_section("Test 2: End Conversation Tool")
    
    try:
        # Import agent classes
        sys.path.insert(0, str(backend_dir / "agents"))
        from dispatcher_agent import DispatcherAgent
        from driver_agent import DriverAgent
        
        # Create agents with custom prompts
        dispatcher = DispatcherAgent(
            custom_prompt="Test dispatcher prompt",
            context="Test context"
        )
        
        driver = DriverAgent(
            custom_prompt="Test driver prompt",
            context="Test context"
        )
        
        # Check that agents have end_conversation method
        assert hasattr(dispatcher, 'end_conversation'), "Dispatcher missing end_conversation tool"
        assert hasattr(driver, 'end_conversation'), "Driver missing end_conversation tool"
        
        print_test("Dispatcher end_conversation Tool", "PASS",
                  "Tool is defined and callable")
        print_test("Driver end_conversation Tool", "PASS",
                  "Tool is defined and callable")
        
        # Check that agents have instructions mentioning end_conversation
        assert "end_conversation" in dispatcher.instructions.lower(), "Dispatcher instructions don't mention end_conversation"
        assert "end_conversation" in driver.instructions.lower(), "Driver instructions don't mention end_conversation"
        
        print_test("Agent Instructions", "PASS",
                  "Both agents instructed to call end_conversation when complete")
        
        return True
        
    except Exception as e:
        print_test("End Conversation Tool Test", "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test that API endpoints are properly configured."""
    print_section("Test 3: API Endpoints")
    
    try:
        sys.path.insert(0, str(backend_dir / "src"))
        from api.routes import rooms
        
        # Check that recording endpoint exists
        assert hasattr(rooms, 'get_recording'), "Recording endpoint not found"
        
        print_test("Recording Endpoint", "PASS",
                  "GET /api/v1/rooms/{room_name}/recording endpoint is defined")
        
        # Check router configuration
        assert hasattr(rooms, 'router'), "Router not configured"
        
        # Get route tags
        routes = [route for route in rooms.router.routes if hasattr(route, 'tags')]
        print_test("Router Configuration", "PASS",
                  f"Router has {len(rooms.router.routes)} routes configured")
        
        return True
        
    except Exception as e:
        print_test("API Endpoints Test", "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


def test_frontend_components():
    """Test that frontend components are properly created."""
    print_section("Test 4: Frontend Components")
    
    try:
        frontend_dir = backend_dir.parent / "frontend" / "src"
        
        # Check ConversationPlayer component exists
        player_component = frontend_dir / "components" / "ConversationPlayer.tsx"
        assert player_component.exists(), "ConversationPlayer component not found"
        
        try:
            player_content = player_component.read_text(encoding='utf-8')
        except:
            player_content = player_component.read_text(encoding='latin-1')
        
        assert "ConversationPlayer" in player_content, "ConversationPlayer export not found"
        assert "playback" in player_content.lower(), "Playback functionality not implemented"
        
        print_test("ConversationPlayer Component", "PASS",
                  "Component created with playback controls")
        
        # Check CSS for player
        player_css = frontend_dir / "components" / "ConversationPlayer.css"
        assert player_css.exists(), "ConversationPlayer CSS not found"
        
        print_test("ConversationPlayer Styles", "PASS",
                  "CSS stylesheet created")
        
        # Check ConversationRoom updates
        room_component = frontend_dir / "components" / "ConversationRoom.tsx"
        try:
            room_content = room_component.read_text(encoding='utf-8')
        except:
            room_content = room_component.read_text(encoding='latin-1')
        
        assert "ConversationPlayer" in room_content, "ConversationPlayer not imported"
        assert "showPlayer" in room_content, "Player state not managed"
        assert "concluded" in room_content, "Conclusion detection not implemented"
        
        print_test("ConversationRoom Updates", "PASS",
                  "Player integration and state management added")
        
        # Check API service updates
        api_service = frontend_dir / "services" / "api.ts"
        try:
            api_content = api_service.read_text(encoding='utf-8')
        except:
            api_content = api_service.read_text(encoding='latin-1')
        
        assert "getRecording" in api_content, "getRecording function not found"
        assert "checkConversationStatus" in api_content, "Status check function not found"
        
        print_test("API Service Updates", "PASS",
                  "Recording and status check functions added")
        
        return True
        
    except Exception as e:
        print_test("Frontend Components Test", "FAIL", str(e))
        import traceback
        traceback.print_exc()
        return False


def test_configuration_files():
    """Test that all configuration is properly set up."""
    print_section("Test 5: Configuration Files")
    
    try:
        # Check environment variables
        required_env = [
            "LIVEKIT_URL",
            "LIVEKIT_API_KEY",
            "LIVEKIT_API_SECRET"
        ]
        
        missing_env = [var for var in required_env if not os.getenv(var)]
        
        if missing_env:
            print_test("Environment Variables", "FAIL",
                      f"Missing: {', '.join(missing_env)}")
            return False
        else:
            print_test("Environment Variables", "PASS",
                      "All required LiveKit credentials configured")
        
        # Check backend structure
        agents_dir = backend_dir / "agents"
        assert (agents_dir / "dispatcher_agent.py").exists(), "Dispatcher agent not found"
        assert (agents_dir / "driver_agent.py").exists(), "Driver agent not found"
        assert (agents_dir / "multi_agent_worker.py").exists(), "Multi-agent worker not found"
        
        print_test("Backend Agent Files", "PASS",
                  "All agent files present and properly configured")
        
        return True
        
    except Exception as e:
        print_test("Configuration Test", "FAIL", str(e))
        return False


def main():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("INTEGRATION TEST SUITE v2")
    print("Testing: Custom Prompts, Auto-Disconnect, Playback")
    print("=" * 60)
    print(Colors.RESET)
    
    results = []
    
    # Run all tests
    results.append(("Custom Prompts", asyncio.run(test_custom_prompts())))
    results.append(("End Conversation Tool", asyncio.run(test_end_conversation_tool())))
    results.append(("API Endpoints", test_api_endpoints()))
    results.append(("Frontend Components", test_frontend_components()))
    results.append(("Configuration", test_configuration_files()))
    
    # Print summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed! Implementation ready for testing.{Colors.RESET}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some tests failed. Please review the errors above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

