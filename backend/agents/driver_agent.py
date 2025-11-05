"""Driver Agent Worker using LiveKit Agents + OpenAI Realtime API."""
import asyncio
import logging
from pathlib import Path
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.plugins import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file, override=True)

logger = logging.getLogger("driver-agent")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    """
    Driver agent entrypoint.
    
    This agent joins a LiveKit room and acts as the driver using OpenAI Realtime API.
    """
    logger.info(f"Driver agent starting in room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    
    # Get scenario and configuration from room metadata
    metadata = ctx.room.metadata
    logger.info(f"Room metadata: {metadata}")
    
    system_prompt = """You are Chris, an experienced truck driver who is currently on the road.
    A dispatcher named Tim from Dispatch Co is calling you about a load opportunity.
    
    Your personality:
    - Professional and efficient
    - Ask relevant questions about the load
    - Care about pickup times, delivery deadlines, and rates
    - Generally agreeable if the load makes sense
    - Respond naturally and conversationally
    
    Ask questions like:
    - What's the pickup window?
    - What's the rate?
    - Is it live load or drop?
    - Any special requirements?
    
    Once you have the details and they sound good, agree to take the load.
    Keep responses brief and natural, like a real phone conversation.
    """
    
    # Create the agent session with OpenAI Realtime
    logger.info("Creating agent session with OpenAI Realtime API...")
    
    # OpenAI Realtime API has built-in VAD, so we don't need separate VAD
    # Instructions/system prompt should be passed via AgentSession initial_prompts
    agent = agents.voice.AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-10-01",
            voice="echo",  # Different voice from dispatcher
            temperature=0.8,
        ),
        initial_prompts=[agents.llm.ChatMessage(role="system", content=system_prompt)],
    )
    
    # Start the agent
    agent.start(ctx.room)
    
    logger.info("Driver agent is active and listening")
    
    # The driver will respond when the dispatcher speaks
    # No need to initiate - just listen and respond
    
    # Keep the agent running
    await asyncio.sleep(600)  # Run for 10 minutes max


if __name__ == "__main__":
    import sys
    # Worker options
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        worker_type=agents.WorkerType.ROOM,
    )
    
    # Run the worker with CLI
    # Usage: python agents/driver_agent.py dev
    # The CLI will automatically use sys.argv for command-line arguments
    cli.run_app(worker_opts)

