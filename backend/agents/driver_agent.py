"""Driver Agent Worker using LiveKit Agents + OpenAI Realtime API."""
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
import json

from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession, Agent
from livekit.agents.llm import function_tool
from livekit.plugins import openai, silero
from conversation_state import get_shared_state

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file, override=True)

logger = logging.getLogger("driver-agent")
logger.setLevel(logging.INFO)


class DriverAgent(Agent):
    """Chris - The Driver Agent"""
    
    def __init__(self, custom_prompt: str = None, context: str = None, conversation_context: str = "") -> None:
        logger.info(f"=== DRIVER AGENT INIT ===")
        logger.info(f"custom_prompt type: {type(custom_prompt)}")
        logger.info(f"custom_prompt value: {repr(custom_prompt)[:100] if custom_prompt else 'None'}")
        logger.info(f"custom_prompt truthy: {bool(custom_prompt)}")
        logger.info(f"context: {repr(context)[:50] if context else 'None'}")
        
        # Use custom prompt from UI if provided, otherwise use default
        if custom_prompt:
            base_instructions = custom_prompt
            logger.info(f"✓ USING CUSTOM PROMPT (length: {len(custom_prompt)})")
        else:
            base_instructions = """You are Chris, an experienced truck driver who is currently on the road.
A dispatcher named Tim from Dispatch Co is calling you about a load opportunity.

Your personality:
- Professional and efficient
- Ask relevant questions about the load
- Care about pickup times, delivery deadlines, and rates
- Generally agreeable if the load makes sense
- Respond naturally and conversationally

CRITICAL INSTRUCTIONS:
- Listen carefully to what Tim says - reference what he told you
- Don't just ask questions - wait for answers to your questions
- If Tim answers something you asked, acknowledge it and move forward
- Respond directly to what Tim is asking
- Consider the information Tim provides when making decisions
- Keep responses brief and natural, like a real phone conversation

Questions to ask (if not already answered):
- What's the pickup window?
- What's the rate?
- Is it live load or drop?
- Any special requirements?

Once you have the details and they sound good, agree to take the load."""
        
        # Add context if provided
        if context:
            base_instructions += f"\n\nContext: {context}"
        
        # Add conversation history for context awareness
        if conversation_context:
            base_instructions += f"\n\nConversation so far:\n{conversation_context}"
        
        base_instructions += """

When the conversation is complete (you've either accepted or rejected the load and there's nothing more to discuss), call the end_conversation tool."""
        
        logger.info(f"Final instructions length: {len(base_instructions)} chars")
        logger.info(f"First 150 chars: {base_instructions[:150]}")
        
        super().__init__(
            instructions=base_instructions
        )
    
    @function_tool
    async def check_availability(self, date: str):
        """Check driver's availability for a specific date."""
        logger.info(f"Checking availability for {date}")
        return f"Available on {date}"
    
    @function_tool
    async def calculate_distance(self, origin: str, destination: str):
        """Calculate approximate distance between two locations."""
        logger.info(f"Calculating distance from {origin} to {destination}")
        return "Approximately 800 miles"
    
    @function_tool
    async def accept_load(self, load_id: str):
        """Accept a load assignment."""
        logger.info(f"Driver accepting load {load_id}")
        return f"Load {load_id} accepted. Ready to proceed."
    
    @function_tool
    async def end_conversation(self, summary: str = ""):
        """End the conversation - both agents should disconnect."""
        logger.info(f"=== DRIVER CALLING END CONVERSATION ===")
        logger.info(f"Summary: {summary}")
        
        shared_state = get_shared_state()
        await shared_state.set_concluded(True)
        
        # Disconnect both agents
        logger.info("Disconnecting both agents...")
        await shared_state.disconnect_all()
        
        return "Conversation ended. Disconnecting both agents."


async def entrypoint(ctx: JobContext):
    """
    Driver agent entrypoint.
    """
    logger.info(f"=== DRIVER AGENT STARTING ===")
    logger.info(f"Room: {ctx.room.name}")
    
    # Read custom prompt and context from room metadata
    custom_prompt = None
    context = None
    
    try:
        if ctx.room.metadata:
            metadata = json.loads(ctx.room.metadata)
            driver_config = metadata.get("driverAgent", {})
            custom_prompt = driver_config.get("prompt")
            context = driver_config.get("actingNotes")
            logger.info(f"Custom driver prompt loaded from room metadata")
            if context:
                logger.info(f"Context: {context[:100]}...")
    except Exception as e:
        logger.warning(f"Could not parse room metadata: {e}")
    
    # Create the agent session with OpenAI Realtime API
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="echo",  # Different voice from dispatcher
            temperature=0.8,
        ),
    )
    
    # Store session in shared state
    shared_state = get_shared_state()
    await shared_state.set_driver_session(session)
    await shared_state.set_room(ctx.room)
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=DriverAgent(custom_prompt=custom_prompt, context=context))
    
    logger.info("Driver agent session started and listening")
    
    # Log current participants
    participants = list(ctx.room.remote_participants.values())
    logger.info(f"Current participants in room: {len(participants)}")
    for p in participants:
        logger.info(f"  - {p.identity} ({p.name or 'no name'})")
    
    # Wait for conversation to flow naturally
    # Driver will respond automatically to dispatcher's messages
    # Keep session active and monitoring
    max_wait = 300  # 5 minute timeout
    elapsed = 0
    
    while not await shared_state.is_concluded() and elapsed < max_wait:
        await asyncio.sleep(0.5)
        elapsed += 0.5
    
    logger.info(f"Driver concluding - closing session (waited {elapsed:.1f}s)")


if __name__ == "__main__":
    # Worker options - no agent_name to allow multiple workers per room
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/driver_agent.py dev
    cli.run_app(worker_opts)

