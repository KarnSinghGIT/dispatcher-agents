"""Dispatcher Agent Worker using LiveKit Agents + OpenAI Realtime API."""
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

logger = logging.getLogger("dispatcher-agent")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    """
    Dispatcher agent entrypoint.
    
    This agent joins a LiveKit room and acts as the dispatcher using OpenAI Realtime API.
    """
    logger.info(f"Dispatcher agent starting in room: {ctx.room.name}")
    
    # Connect to the room
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    
    # Get scenario and configuration from room metadata
    metadata = ctx.room.metadata
    logger.info(f"Room metadata: {metadata}")
    
    # Parse metadata to get scenario details
    # In production, parse JSON from metadata
    # For now, use a default prompt
    
    system_prompt = """You are Tim, a friendly and professional dispatcher at Dispatch Co. 
    You are calling a driver named Chris about a load opportunity.
    
    Your goal is to:
    1. Greet Chris warmly
    2. Present the load details clearly
    3. Answer any questions he has
    4. Get his commitment to take the load
    5. Provide next steps
    
    Be conversational, professional, and efficient. Keep responses natural and brief.
    Wait for responses before continuing.
    
    The load details:
    - Load ID: HDX-2478
    - Type: HVAC units, 42,000 lbs
    - Pickup: Dallas TX, 8 AM tomorrow (live load)
    - Delivery: Atlanta GA, before noon next day
    - Trailer: Dry van
    - Rate: $2.10/mile ($1,680 total, all-in)
    - Requirements: Two-strap securement, Macro-1 update when empty
    """
    
    # Create the agent session with OpenAI Realtime
    logger.info("Creating agent session with OpenAI Realtime API...")
    
    # Create RealtimeModel with system instructions
    # For OpenAI Realtime API, we need to pass instructions through the model's chat context
    realtime_model = openai.realtime.RealtimeModel(
        model="gpt-4o-realtime-preview-2024-10-01",
        voice="alloy",
        temperature=0.8,
    )
    
    # Create AgentSession with the model
    agent = agents.voice.AgentSession(
        llm=realtime_model,
    )
    
    # Start the agent
    agent.start(ctx.room)
    
    # Add system prompt to the chat context after session starts
    # The agent's LLM chat context can be accessed and modified
    if hasattr(agent, 'llm') and hasattr(agent.llm, 'chat'):
        agent.llm.chat.add_message(role="system", content=system_prompt)
    
    logger.info("Dispatcher agent is active and ready")
    
    # Keep the agent running - OpenAI Realtime will handle conversation automatically
    await asyncio.sleep(600)  # Run for 10 minutes max


if __name__ == "__main__":
    import sys
    # Worker options
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        worker_type=agents.WorkerType.ROOM,
    )
    
    # Run the worker with CLI
    # Usage: python agents/dispatcher_agent.py dev
    # The CLI will automatically use sys.argv for command-line arguments
    cli.run_app(worker_opts)

