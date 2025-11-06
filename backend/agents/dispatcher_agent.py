"""Dispatcher Agent Worker using LiveKit Agents + OpenAI Realtime API."""
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

logger = logging.getLogger("dispatcher-agent")
logger.setLevel(logging.INFO)


class DispatcherAgent(Agent):
    """Tim - The Dispatcher Agent"""
    
    def __init__(self, custom_prompt: str = None, context: str = None, conversation_context: str = "") -> None:
        # Use custom prompt from UI if provided, otherwise use default
        if custom_prompt:
            base_instructions = custom_prompt
        else:
            base_instructions = """You are Tim, a friendly and professional dispatcher at Dispatch Co. 
You are calling a driver named Chris about a load opportunity.

Your goal is to:
1. Greet Chris warmly
2. Present the load details clearly
3. Answer any questions he has - LISTEN CAREFULLY to what Chris asks
4. Get his commitment to take the load
5. Provide next steps

CRITICAL INSTRUCTIONS:
- Listen carefully to everything Chris says
- If Chris asks a question, ALWAYS answer it directly
- If Chris has concerns, address those concerns before moving forward
- Don't rush to book the load - first understand if Chris is interested
- Reference previous parts of the conversation if relevant
- Keep responses natural and brief
- Wait for responses before continuing"""
        
        # Add context if provided
        if context:
            base_instructions += f"\n\nContext: {context}"
        
        # Add conversation history for context awareness
        if conversation_context:
            base_instructions += f"\n\nConversation so far:\n{conversation_context}"
        
        base_instructions += """

IMPORTANT: Start the conversation by greeting Chris. Say something like "Hey Chris, this is Tim from Dispatch Co. I've got a load opportunity for you."

When you have successfully completed the call (got agreement from the driver, or determined they won't take it), call the end_conversation tool."""
        
        super().__init__(
            instructions=base_instructions
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
        return f"Load {load_id}: Dallas TX to Atlanta GA, 42,000 lbs HVAC units, $2.10/mile"
    
    @function_tool
    async def end_conversation(self, summary: str = ""):
        """End the conversation - both agents should disconnect."""
        logger.info(f"=== DISPATCHER CALLING END CONVERSATION ===")
        logger.info(f"Summary: {summary}")
        
        shared_state = get_shared_state()
        await shared_state.set_concluded(True)
        
        # Disconnect both agents
        logger.info("Disconnecting both agents...")
        await shared_state.disconnect_all()
        
        return "Conversation ended. Disconnecting both agents."


async def entrypoint(ctx: JobContext):
    """
    Dispatcher agent entrypoint.
    """
    logger.info(f"=== DISPATCHER AGENT STARTING ===")
    logger.info(f"Room: {ctx.room.name}")
    
    # Read custom prompt and context from room metadata
    custom_prompt = None
    context = None
    
    try:
        if ctx.room.metadata:
            metadata = json.loads(ctx.room.metadata)
            dispatcher_config = metadata.get("dispatcherAgent", {})
            custom_prompt = dispatcher_config.get("prompt")
            context = dispatcher_config.get("actingNotes")
            logger.info(f"Custom dispatcher prompt loaded from room metadata")
            if context:
                logger.info(f"Context: {context[:100]}...")
    except Exception as e:
        logger.warning(f"Could not parse room metadata: {e}")
    
    # Create the agent session with OpenAI Realtime API
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview-2024-12-17",
            voice="alloy",
            temperature=0.8,
        ),
    )
    
    # Store session in shared state
    shared_state = get_shared_state()
    await shared_state.set_dispatcher_session(session)
    await shared_state.set_room(ctx.room)
    
    # Start the session with the agent
    await session.start(room=ctx.room, agent=DispatcherAgent(custom_prompt=custom_prompt, context=context))
    
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
    
    # Monitor for conversation conclusion
    max_wait = 300  # 5 minute timeout
    elapsed = 0
    while not await shared_state.is_concluded() and elapsed < max_wait:
        await asyncio.sleep(0.5)
        elapsed += 0.5
    
    logger.info(f"Dispatcher concluding - closing session (waited {elapsed:.1f}s)")


if __name__ == "__main__":
    # Worker options - no agent_name to allow multiple workers per room
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
    )
    
    # Run the worker with CLI
    # Usage: python agents/dispatcher_agent.py dev
    cli.run_app(worker_opts)

