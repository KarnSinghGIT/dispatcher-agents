"""
Multi-Agent Worker - Runs both Dispatcher and Driver agents in the same room.

This worker manages both agents in a single process to ensure they both join the same room.
"""

import asyncio
import logging
from livekit import rtc
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero
from typing import Dict, Any

from dispatcher_agent import DispatcherAgent
from driver_agent import DriverAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Multi-agent entrypoint that runs both dispatcher and driver agents in the same room.
    """
    logger.info(f"=== MULTI-AGENT WORKER STARTING ===")
    logger.info(f"Room: {ctx.room.name}")
    
    # Get room metadata
    room_metadata = ctx.room.metadata
    if room_metadata:
        try:
            import json
            metadata = json.loads(room_metadata)
            logger.info(f"Room metadata: {metadata.get('scenario', {}).get('loadId', 'unknown')}")
        except:
            pass
    
    # Create two separate agent sessions
    # Session 1: Dispatcher Agent
    dispatcher_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="alloy",
            temperature=0.8,
        ),
        # vad=silero.VAD.load(),  # Uncomment if VAD is needed
    )
    
    # Session 2: Driver Agent
    driver_session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="echo",
            temperature=0.7,
        ),
        # vad=silero.VAD.load(),  # Uncomment if VAD is needed
    )
    
    logger.info("Starting both agent sessions...")
    
    # Start dispatcher session
    logger.info("Starting dispatcher session...")
    await dispatcher_session.start(room=ctx.room, agent=DispatcherAgent())
    logger.info("✓ Dispatcher agent session started")
    
    # Start driver session
    logger.info("Starting driver session...")
    await driver_session.start(room=ctx.room, agent=DriverAgent())
    logger.info("✓ Driver agent session started")
    
    # Log current participants
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Current participants in room: {len(participants)}")
    for p in participants:
        logger.info(f"  - {p.identity} ({p.name or 'no name'})")
    
    logger.info("Multi-agent worker ready - both agents active and listening")
    
    # Keep both agents responding in a loop
    logger.info("Starting continuous conversation loop...")
    
    # Dispatcher initiates the first reply
    logger.info("Dispatcher initiating conversation...")
    await dispatcher_session.generate_reply()
    
    # Now both agents will automatically respond to each other
    # Keep the sessions active by continuously generating replies
    max_turns = 20  # Prevent infinite loops, allow up to 20 exchanges
    turn_count = 0
    
    while turn_count < max_turns:
        # Driver responds to dispatcher
        logger.info(f"Turn {turn_count + 1}: Driver generating response...")
        await driver_session.generate_reply()
        turn_count += 1
        
        if turn_count >= max_turns:
            break
            
        # Dispatcher responds to driver
        logger.info(f"Turn {turn_count + 1}: Dispatcher generating response...")
        await dispatcher_session.generate_reply()
        turn_count += 1
    
    logger.info("Conversation completed - agents finished exchanging")


if __name__ == "__main__":
    # Single worker that manages both agents
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/multi_agent_worker.py dev
    cli.run_app(worker_opts)

