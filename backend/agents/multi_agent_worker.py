"""
Multi-Agent Worker - Runs both Dispatcher and Driver agents in the same room.

This worker manages both agents in a single process to ensure they both join the same room.
The agents use tool calling to detect when the conversation is complete and automatically disconnect.
"""

import asyncio
import logging
from livekit import rtc
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero
from typing import Dict, Any
import json

from dispatcher_agent import DispatcherAgent
from driver_agent import DriverAgent
from conversation_state import get_shared_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Multi-agent entrypoint that runs both dispatcher and driver agents in the same room.
    Uses tool calling for agents to signal conversation completion and auto-disconnect.
    """
    logger.info(f"=== MULTI-AGENT WORKER STARTING ===")
    logger.info(f"Room: {ctx.room.name}")
    
    # Get room metadata - with retry for race condition
    room_metadata = ctx.room.metadata
    dispatcher_config = {}
    driver_config = {}
    
    logger.info(f"=== CHECKING ROOM METADATA ===")
    logger.info(f"Initial metadata length: {len(room_metadata) if room_metadata else 0} bytes")
    
    # CRITICAL FIX: If metadata is empty, fetch room details from LiveKit API
    # This handles the race condition where worker joins before metadata is propagated
    if not room_metadata or len(room_metadata) == 0:
        logger.info("⚠️ Metadata empty on initial join, fetching from LiveKit API...")
        try:
            import os
            from livekit import api as livekit_api
            from dotenv import load_dotenv
            from pathlib import Path
            import asyncio
            
            # Load env
            backend_dir = Path(__file__).parent.parent
            env_file = backend_dir / ".env"
            load_dotenv(dotenv_path=env_file, override=True)
            
            livekit_url = os.getenv("LIVEKIT_URL")
            api_key = os.getenv("LIVEKIT_API_KEY")
            api_secret = os.getenv("LIVEKIT_API_SECRET")
            
            if all([livekit_url, api_key, api_secret]):
                lk_api = livekit_api.LiveKitAPI(
                    url=livekit_url,
                    api_key=api_key,
                    api_secret=api_secret
                )
                
                # Retry loop - sometimes metadata takes a moment to propagate
                max_retries = 5
                retry_delay = 0.5  # seconds
                
                for attempt in range(max_retries):
                    logger.info(f"Fetching rooms (attempt {attempt + 1}/{max_retries})...")
                    
                    # Fetch room details
                    rooms_response = await lk_api.room.list_rooms(livekit_api.ListRoomsRequest())
                    
                    logger.info(f"Found {len(rooms_response.rooms)} rooms")
                    
                    # Access the rooms attribute of the response
                    room_found = False
                    for room in rooms_response.rooms:
                        logger.info(f"  Room: {room.name}, metadata length: {len(room.metadata) if room.metadata else 0}")
                        if room.name == ctx.room.name:
                            room_found = True
                            if room.metadata and len(room.metadata) > 0:
                                room_metadata = room.metadata
                                logger.info(f"✓ Fetched metadata from API: {len(room_metadata)} bytes")
                                break
                            else:
                                logger.info(f"  Room found but metadata still empty, will retry...")
                    
                    if room_metadata and len(room_metadata) > 0:
                        break  # Got metadata, exit retry loop
                    
                    if not room_found:
                        logger.warning(f"  Room {ctx.room.name} not found in list yet")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                
                await lk_api.aclose()
        except Exception as e:
            logger.warning(f"Could not fetch room metadata from API: {e}")
            import traceback
            logger.warning(traceback.format_exc())
    
    logger.info(f"Final metadata length: {len(room_metadata) if room_metadata else 0} bytes")
    
    if room_metadata:
        try:
            metadata = json.loads(room_metadata)
            logger.info(f"✓ Metadata parsed successfully")
            logger.info(f"Room metadata: {metadata.get('scenario', {}).get('loadId', 'unknown')}")
            
            dispatcher_config = metadata.get("dispatcherAgent", {})
            driver_config = metadata.get("driverAgent", {})
            
            logger.info(f"Dispatcher config keys: {list(dispatcher_config.keys())}")
            logger.info(f"Driver config keys: {list(driver_config.keys())}")
        except Exception as e:
            logger.warning(f"Could not parse room metadata: {e}")
    
    # Note: Sessions are created first, then we'll set instructions after agent creation
    # This is a placeholder that will be updated once we have the agent instructions
    
    logger.info("Starting both agent sessions...")
    
    # Get custom prompts if available
    logger.info(f"=== EXTRACTING PROMPTS FROM CONFIG ===")
    logger.info(f"dispatcher_config type: {type(dispatcher_config)}")
    logger.info(f"dispatcher_config content: {dispatcher_config}")
    logger.info(f"driver_config type: {type(driver_config)}")
    logger.info(f"driver_config content: {driver_config}")
    
    custom_dispatcher_prompt = dispatcher_config.get("prompt")
    custom_dispatcher_context = dispatcher_config.get("actingNotes")
    custom_driver_prompt = driver_config.get("prompt")
    custom_driver_context = driver_config.get("actingNotes")
    
    logger.info(f"=== CUSTOM PROMPTS ===")
    logger.info(f"Extracted dispatcher prompt: {repr(custom_dispatcher_prompt)[:200]}")
    logger.info(f"Dispatcher custom prompt: {'YES' if custom_dispatcher_prompt else 'NO'}")
    if custom_dispatcher_prompt:
        logger.info(f"  Length: {len(custom_dispatcher_prompt)} chars")
        logger.info(f"  Preview: {custom_dispatcher_prompt[:100]}...")
    logger.info(f"Dispatcher context: {'YES' if custom_dispatcher_context else 'NO'}")
    
    logger.info(f"Extracted driver prompt: {repr(custom_driver_prompt)[:200]}")
    logger.info(f"Driver custom prompt: {'YES' if custom_driver_prompt else 'NO'}")
    if custom_driver_prompt:
        logger.info(f"  Length: {len(custom_driver_prompt)} chars")
        logger.info(f"  Preview: {custom_driver_prompt[:100]}...")
    logger.info(f"Driver context: {'YES' if custom_driver_context else 'NO'}")
    
    # DEBUG: Log what we're passing to agents
    logger.info(f"=== PASSING TO AGENTS ===")
    logger.info(f"About to create DispatcherAgent with custom_prompt={custom_dispatcher_prompt is not None}")
    logger.info(f"About to create DriverAgent with custom_prompt={custom_driver_prompt is not None}")
    
    # Create agent instances first to get their instructions
    dispatcher_agent = DispatcherAgent(
        custom_prompt=custom_dispatcher_prompt,
        context=custom_dispatcher_context
    )
    driver_agent = DriverAgent(
        custom_prompt=custom_driver_prompt,
        context=custom_driver_context
    )
    
    logger.info(f"Dispatcher agent instructions length: {len(dispatcher_agent.instructions)} chars")
    logger.info(f"Driver agent instructions length: {len(driver_agent.instructions)} chars")
    
    # Create agent sessions
    # Note: Instructions will be applied when session.start() is called with the agent
    logger.info("Creating agent sessions...")
    dispatcher_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="alloy",
            temperature=0.8,
        ),
    )
    
    driver_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="echo",
            temperature=0.7,
        ),
    )
    
    # Start dispatcher session
    logger.info("Starting dispatcher session...")
    await dispatcher_session.start(
        room=ctx.room, 
        agent=dispatcher_agent
    )
    logger.info("✓ Dispatcher agent session started")
    
    # CRITICAL: Explicitly set session instructions after start
    # The session should use agent instructions, but we ensure it here
    logger.info("Ensuring dispatcher session uses agent instructions...")
    try:
        # Try to update session instructions if method exists
        await dispatcher_session.update_instructions(dispatcher_agent.instructions)
        logger.info("✓ Dispatcher instructions updated via update_instructions()")
    except AttributeError:
        logger.info("Note: update_instructions() not available, relying on agent's instructions")
    
    # Start driver session
    logger.info("Starting driver session...")
    await driver_session.start(
        room=ctx.room, 
        agent=driver_agent
    )
    logger.info("✓ Driver agent session started")
    
    # CRITICAL: Explicitly set session instructions after start
    logger.info("Ensuring driver session uses agent instructions...")
    try:
        # Try to update session instructions if method exists
        await driver_session.update_instructions(driver_agent.instructions)
        logger.info("✓ Driver instructions updated via update_instructions()")
    except AttributeError:
        logger.info("Note: update_instructions() not available, relying on agent's instructions")
    
    # Log current participants
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Current participants in room: {len(participants)}")
    for p in participants:
        logger.info(f"  - {p.identity} ({p.name or 'no name'})")
    
    logger.info("Multi-agent worker ready - both agents active and listening")
    
    # Reset shared state for this new conversation
    shared_state = get_shared_state()
    await shared_state.reset()
    logger.info("✓ Conversation state reset for new conversation")
    
    # Dispatcher initiates the first reply
    logger.info("Dispatcher initiating conversation...")
    try:
        await dispatcher_session.generate_reply()
        logger.info("✓ Dispatcher spoke successfully")
        # Capture dispatcher's initial greeting
        await shared_state.add_message("Tim (Dispatcher)", "Initiated greeting")
    except Exception as e:
        logger.error(f"❌ Dispatcher failed to speak: {e}")
        import traceback
        traceback.print_exc()
        return
    
    logger.info("Starting natural conversation flow - agents will conclude when ready...")
    
    # shared_state already initialized above
    turn_count = 0
    max_duration_seconds = 600  # 10 minute safety timeout
    start_time = asyncio.get_event_loop().time()
    
    # Keep agents conversing naturally until they decide to end
    while not await shared_state.is_concluded():
        # Check safety timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > max_duration_seconds:
            logger.warning(f"⚠️ Conversation reached safety timeout ({max_duration_seconds}s)")
            break
        
        # Wait a bit for response processing
        await asyncio.sleep(2)
        
        # Driver responds
        logger.info(f"Turn {turn_count + 1}: Driver generating response...")
        try:
            # Get conversation context for driver awareness
            conversation_context = await shared_state.format_conversation_context()
            
            # Create fresh driver agent instance with current conversation context
            updated_driver_agent = DriverAgent(
                custom_prompt=custom_driver_prompt,
                context=custom_driver_context,
                conversation_context=conversation_context
            )
            
            # Update the session with new agent instance AND update LLM instructions
            driver_session._agent = updated_driver_agent
            # CRITICAL: Also update the LLM instructions to reflect the new context
            if hasattr(driver_session._llm, 'update_instructions'):
                driver_session._llm.update_instructions(updated_driver_agent.instructions)
            elif hasattr(driver_session._llm, '_instructions'):
                driver_session._llm._instructions = updated_driver_agent.instructions
            
            await driver_session.generate_reply()
            logger.info(f"✓ Driver spoke")
            # Capture driver response
            await shared_state.add_message("Chris (Driver)", "Responded to dispatcher")
            turn_count += 1
        except Exception as e:
            logger.error(f"❌ Driver response error: {e}")
            import traceback
            traceback.print_exc()
            break
        
        # Check if agents concluded
        if await shared_state.is_concluded():
            logger.info("✓ Agent signaled conversation conclusion")
            break
        
        await asyncio.sleep(2)
        
        # Dispatcher responds
        logger.info(f"Turn {turn_count + 1}: Dispatcher generating response...")
        try:
            # Get conversation context for dispatcher awareness
            conversation_context = await shared_state.format_conversation_context()
            
            # Create fresh dispatcher agent instance with current conversation context
            updated_dispatcher_agent = DispatcherAgent(
                custom_prompt=custom_dispatcher_prompt,
                context=custom_dispatcher_context,
                conversation_context=conversation_context
            )
            
            # Update the session with new agent instance AND update LLM instructions
            dispatcher_session._agent = updated_dispatcher_agent
            # CRITICAL: Also update the LLM instructions to reflect the new context
            if hasattr(dispatcher_session._llm, 'update_instructions'):
                dispatcher_session._llm.update_instructions(updated_dispatcher_agent.instructions)
            elif hasattr(dispatcher_session._llm, '_instructions'):
                dispatcher_session._llm._instructions = updated_dispatcher_agent.instructions
            
            await dispatcher_session.generate_reply()
            logger.info(f"✓ Dispatcher spoke")
            # Capture dispatcher response
            await shared_state.add_message("Tim (Dispatcher)", "Responded to driver")
            turn_count += 1
        except Exception as e:
            logger.error(f"❌ Dispatcher response error: {e}")
            import traceback
            traceback.print_exc()
            break
        
        # Check if agents concluded
        if await shared_state.is_concluded():
            logger.info("✓ Agent signaled conversation conclusion")
            break
        
        # Log progress every 10 turns
        if turn_count % 10 == 0:
            logger.info(f"📊 Conversation ongoing... {turn_count} turns so far")
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"✅ Conversation completed: {turn_count} turns in {elapsed_time:.1f}s")
    
    # Save conversation to file for later retrieval
    try:
        conversation_file = await shared_state.save_conversation_to_file(ctx.room.name)
        logger.info(f"✓ Conversation saved: {conversation_file}")
    except Exception as e:
        logger.warning(f"⚠️ Could not save conversation: {e}")
    
    logger.info("Multi-agent worker conversation complete")


if __name__ == "__main__":
    # Single worker that manages both agents
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/multi_agent_worker.py dev
    cli.run_app(worker_opts)

