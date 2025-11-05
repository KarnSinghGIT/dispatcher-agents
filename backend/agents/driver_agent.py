"""Driver Agent Worker using LiveKit Agents + OpenAI Realtime API."""
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

logger = logging.getLogger("driver-agent")
logger.setLevel(logging.INFO)


class DriverAgent(Agent):
    """Chris - The Driver Agent"""
    
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are Chris, an experienced truck driver who is currently on the road.
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

Wait for Tim to greet you first, then respond naturally to his questions and information.
"""
        )
    
    @function_tool
    async def check_availability(self, date: str):
        """Check driver's availability for a specific date."""
        logger.info(f"Checking availability for {date}")
        # In production, this would check actual calendar
        return f"Available on {date}"
    
    @function_tool
    async def calculate_distance(self, origin: str, destination: str):
        """Calculate approximate distance between two locations."""
        logger.info(f"Calculating distance from {origin} to {destination}")
        # In production, this would use a real mapping service
        return "Approximately 800 miles"
    
    @function_tool
    async def accept_load(self, load_id: str):
        """Accept a load assignment."""
        logger.info(f"Driver accepting load {load_id}")
        return f"Load {load_id} accepted. Ready to proceed."


async def entrypoint(ctx: JobContext):
    """
    Driver agent entrypoint.
    
    This agent joins a LiveKit room and acts as the driver using OpenAI Realtime API.
    """
    logger.info(f"Driver agent starting in room: {ctx.room.name}")
    
    # Create the agent session with OpenAI Realtime API
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="echo",  # Different voice from dispatcher
            temperature=0.8,
        ),
        # vad=silero.VAD.load(),
    )
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=DriverAgent())
    
    logger.info("Driver agent session started and listening")
    
    # The driver will respond when the dispatcher speaks
    # No need to initiate - just listen and respond


if __name__ == "__main__":
    # Worker options
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/driver_agent.py dev
    cli.run_app(worker_opts)

