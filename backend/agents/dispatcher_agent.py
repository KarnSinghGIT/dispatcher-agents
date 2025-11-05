"""Dispatcher Agent Worker using LiveKit Agents + OpenAI Realtime API."""
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession, Agent
from livekit.agents.llm import function_tool
from livekit.plugins import (
    openai,
    silero
)

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file, override=True)

logger = logging.getLogger("dispatcher-agent")
logger.setLevel(logging.INFO)


class DispatcherAgent(Agent):
    """Tim - The Dispatcher Agent"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Tim, a friendly and professional dispatcher at Dispatch Co. 
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

IMPORTANT: Start the conversation by greeting Chris. Say something like "Hey Chris, this is Tim from Dispatch Co. I've got a load opportunity for you."
"""
        )
    
    @function_tool
    async def mark_load_accepted(self, load_id: str):
        """Mark a load as accepted by the driver."""
        logger.info(f"Load {load_id} has been accepted by driver")
        return f"Load {load_id} marked as accepted"
    
    @function_tool
    async def mark_load_rejected(self, load_id: str, reason: str = ""):
        """Mark a load as rejected by the driver."""
        logger.info(f"Load {load_id} has been rejected. Reason: {reason}")
        return f"Load {load_id} marked as rejected"
    
    @function_tool
    async def get_load_details(self, load_id: str):
        """Get additional details about a specific load."""
        logger.info(f"Fetching details for load {load_id}")
        # In production, this would fetch from a database
        return f"Load {load_id}: Dallas TX to Atlanta GA, 42,000 lbs HVAC units, $2.10/mile"


async def entrypoint(ctx: JobContext):
    """
    Dispatcher agent entrypoint.
    
    This agent joins a LiveKit room and acts as the dispatcher using OpenAI Realtime API.
    """
    logger.info(f"=== DISPATCHER AGENT STARTING ===")
    logger.info(f"Room: {ctx.room.name}")
    logger.info(f"Worker: {ctx.worker.name if hasattr(ctx, 'worker') else 'unknown'}")
    
    # Create the agent session with OpenAI Realtime API
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="alloy",
            temperature=0.8,
        ),
        # vad=silero.VAD.load(),
    )
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=DispatcherAgent())
    
    logger.info("Dispatcher agent session started")
    
    # Log current participants
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Current participants in room: {len(participants)}")
    for p in participants:
        logger.info(f"  - {p.identity} ({p.name or 'no name'})")
    
    # Wait for other participants to join
    await asyncio.sleep(2)
    
    # Check again after delay
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Participants after delay: {len(participants)}")
    for p in participants:
        logger.info(f"  - {p.identity} ({p.name or 'no name'})")
    
    # Generate initial greeting to start the conversation
    await session.generate_reply()
    
    logger.info("Dispatcher agent initiated conversation")


if __name__ == "__main__":
    # Worker options - no agent_name to allow multiple workers per room
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/dispatcher_agent.py dev
    cli.run_app(worker_opts)

