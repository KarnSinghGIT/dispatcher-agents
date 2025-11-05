"""Room management API routes for LiveKit."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import json
from pathlib import Path
from livekit import api
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent.parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file)

router = APIRouter(prefix="/api/v1/rooms", tags=["rooms"])


class Scenario(BaseModel):
    """Load scenario details."""
    loadId: str
    loadType: str
    weight: int
    pickupLocation: str
    pickupTime: str
    pickupType: str
    deliveryLocation: str
    deliveryDeadline: str
    trailerType: str
    ratePerMile: float
    totalRate: float
    accessorials: str
    securementRequirements: str
    tmsUpdate: str


class AgentConfig(BaseModel):
    """Agent configuration."""
    role: str
    prompt: str
    actingNotes: Optional[str] = None


class CreateRoomRequest(BaseModel):
    """Request to create a conversation room."""
    scenario: Scenario
    dispatcherAgent: AgentConfig
    driverAgent: AgentConfig


class RoomInfo(BaseModel):
    """Room information response."""
    roomName: str
    roomToken: str
    livekitUrl: str
    conversationId: str


@router.post("/create", response_model=RoomInfo)
async def create_room(request: CreateRoomRequest):
    """
    Create a LiveKit room for the voice conversation.
    
    This creates a room and generates a token for the frontend to join.
    The agent workers will be dispatched separately.
    """
    try:
        # Get LiveKit credentials
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not all([livekit_url, api_key, api_secret]):
            missing = []
            if not livekit_url:
                missing.append("LIVEKIT_URL")
            if not api_key:
                missing.append("LIVEKIT_API_KEY")
            if not api_secret:
                missing.append("LIVEKIT_API_SECRET")
            
            raise HTTPException(
                status_code=500,
                detail=f"LiveKit credentials not configured. Missing: {', '.join(missing)}"
            )
        
        # Generate unique room name
        conversation_id = f"conv_{request.scenario.loadId}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        room_name = conversation_id
        
        # Create LiveKit API client
        lk_api = api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Prepare metadata as JSON string
        metadata_dict = {
            "scenario": request.scenario.model_dump(),
            "dispatcherAgent": request.dispatcherAgent.model_dump(),
            "driverAgent": request.driverAgent.model_dump()
        }
        metadata_json = json.dumps(metadata_dict)
        
        # Create the room
        room = await lk_api.room.create_room(
            api.CreateRoomRequest(
                name=room_name,
                empty_timeout=600,  # 10 minutes
                max_participants=10,
                metadata=metadata_json
            )
        )
        
        # Generate token for frontend (observer role)
        token = api.AccessToken(api_key, api_secret)
        token.with_identity("observer") \
             .with_name("Observer") \
             .with_grants(api.VideoGrants(
                 room_join=True,
                 room=room_name,
                 can_publish=False,  # Observer can't publish
                 can_subscribe=True  # Observer can subscribe to audio
             ))
        
        # Set token expiry
        token.ttl = timedelta(hours=2)
        
        # Generate JWT token
        jwt_token = token.to_jwt()
        
        await lk_api.aclose()
        
        return RoomInfo(
            roomName=room_name,
            roomToken=jwt_token,
            livekitUrl=livekit_url,
            conversationId=conversation_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating room: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create room: {str(e)}"
        )


@router.get("/{room_name}/status")
async def get_room_status(room_name: str):
    """Get the status of a room."""
    try:
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not all([livekit_url, api_key, api_secret]):
            raise HTTPException(
                status_code=500,
                detail="LiveKit credentials not configured"
            )
        
        lk_api = api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # List participants in the room
        participants = await lk_api.room.list_participants(
            api.ListParticipantsRequest(room=room_name)
        )
        
        await lk_api.aclose()
        
        return {
            "roomName": room_name,
            "participantCount": len(participants),
            "participants": [
                {
                    "identity": p.identity,
                    "name": p.name,
                    "state": str(p.state)
                }
                for p in participants
            ]
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error getting room status: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get room status: {str(e)}"
        )


@router.post("/{room_name}/dispatch-agents")
async def dispatch_agents(room_name: str):
    """
    Dispatch agent workers to the room.
    
    This endpoint provides information about agent dispatch.
    Both agents should be running as workers and will automatically join new rooms.
    Make sure both dispatcher_agent.py and driver_agent.py are running before creating a room.
    """
    try:
        # Check if room exists and get participant count
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if all([livekit_url, api_key, api_secret]):
            lk_api = api.LiveKitAPI(
                url=livekit_url,
                api_key=api_key,
                api_secret=api_secret
            )
            
            try:
                participants = await lk_api.room.list_participants(
                    api.ListParticipantsRequest(room=room_name)
                )
                participant_count = len(participants)
            except:
                participant_count = 0
            
            await lk_api.aclose()
        else:
            participant_count = 0
        
        return {
            "message": "Agent dispatch information",
            "roomName": room_name,
            "currentParticipants": participant_count,
            "instructions": "Ensure both dispatcher_agent.py and driver_agent.py are running. They will automatically join new rooms when created.",
            "expectedAgents": 2,
            "note": "Each agent runs as a separate worker with unique agent_name"
        }
    except Exception as e:
        return {
            "message": "Could not check room status",
            "roomName": room_name,
            "error": str(e),
            "instructions": "Start dispatcher_agent.py and driver_agent.py in separate terminals"
        }
