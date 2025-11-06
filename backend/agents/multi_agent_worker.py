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
    
    # Get room metadata
    room_metadata = ctx.room.metadata
    dispatcher_config = {}
    driver_config = {}
    
    if room_metadata:
        try:
            metadata = json.loads(room_metadata)
            logger.info(f"Room metadata: {metadata.get('scenario', {}).get('loadId', 'unknown')}")
            dispatcher_config = metadata.get("dispatcherAgent", {})
            driver_config = metadata.get("driverAgent", {})
        except Exception as e:
            logger.warning(f"Could not parse room metadata: {e}")
    
    # Create two separate agent sessions
    # Session 1: Dispatcher Agent
    dispatcher_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="alloy",
            temperature=0.8,
        ),
    )
    
    # Session 2: Driver Agent
    driver_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="echo",
            temperature=0.7,
        ),
    )
    
    logger.info("Starting both agent sessions...")
    
    # Get custom prompts if available
    custom_dispatcher_prompt = dispatcher_config.get("prompt")
    custom_dispatcher_context = dispatcher_config.get("actingNotes")
    custom_driver_prompt = driver_config.get("prompt")
    custom_driver_context = driver_config.get("actingNotes")
    
    # Start dispatcher session
    logger.info("Starting dispatcher session...")
    await dispatcher_session.start(
        room=ctx.room, 
        agent=DispatcherAgent(
            custom_prompt=custom_dispatcher_prompt,
            context=custom_dispatcher_context
        )
    )
    logger.info("✓ Dispatcher agent session started")
    
    # Start driver session
    logger.info("Starting driver session...")
    await driver_session.start(
        room=ctx.room, 
        agent=DriverAgent(
            custom_prompt=custom_driver_prompt,
            context=custom_driver_context
        )
    )
    logger.info("✓ Driver agent session started")
    
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
            from driver_agent import DriverAgent
            updated_driver_agent = DriverAgent(
                custom_prompt=custom_driver_prompt,
                context=custom_driver_context,
                conversation_context=conversation_context
            )
            
            # Update the session with new agent instance
            driver_session._agent = updated_driver_agent
            
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
            from dispatcher_agent import DispatcherAgent
            updated_dispatcher_agent = DispatcherAgent(
                custom_prompt=custom_dispatcher_prompt,
                context=custom_dispatcher_context,
                conversation_context=conversation_context
            )
            
            # Update the session with new agent instance
            dispatcher_session._agent = updated_dispatcher_agent
            
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
    logger.info("Multi-agent worker conversation complete")


if __name__ == "__main__":
    # Single worker that manages both agents
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/multi_agent_worker.py dev
    cli.run_app(worker_opts)

