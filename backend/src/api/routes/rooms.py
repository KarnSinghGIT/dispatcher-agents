"""Room management API routes for LiveKit."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import json
from pathlib import Path
from livekit import api
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file in backend directory
# Path: backend/src/api/routes/rooms.py
# Parent dirs: routes -> api -> src -> backend
# We need 4 levels up: rooms.py -> routes/ -> api/ -> src/ -> backend/
backend_dir = Path(__file__).parent.parent.parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file)

print(f"[INIT] rooms.py loaded from: {Path(__file__)}")
print(f"[INIT] Backend directory: {backend_dir}")
print(f"[INIT] Recordings directory will be: {backend_dir / 'recordings'}")

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
        print(f"\n[ROOMS API] Creating room with metadata:")
        print(f"  Request scenario: {request.scenario}")
        print(f"  Request dispatcherAgent: {request.dispatcherAgent}")
        print(f"  Request driverAgent: {request.driverAgent}")
        
        metadata_dict = {
            "scenario": request.scenario.model_dump(),
            "dispatcherAgent": request.dispatcherAgent.model_dump(),
            "driverAgent": request.driverAgent.model_dump()
        }
        metadata_json = json.dumps(metadata_dict)
        
        print(f"  Metadata dict: {metadata_dict}")
        print(f"  Metadata JSON length: {len(metadata_json)} bytes")
        print(f"  Dispatcher config: {metadata_dict.get('dispatcherAgent')}")
        print(f"  Driver config: {metadata_dict.get('driverAgent')}")
        
        # Create the room
        room = await lk_api.room.create_room(
            api.CreateRoomRequest(
                name=room_name,
                empty_timeout=600,  # 10 minutes
                max_participants=10,
                metadata=metadata_json
            )
        )
        
        print(f"  Room created with metadata length: {len(room.metadata) if room.metadata else 0} bytes")
        print(f"  Room metadata: {room.metadata[:200] if room.metadata else 'EMPTY'}")
        
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


@router.get("/{room_name}/transcript")
async def get_transcript(room_name: str):
    """
    Get the conversation transcript for a completed conversation.
    
    This retrieves the saved JSON file with all conversation messages.
    """
    try:
        # Recordings directory inside backend
        recordings_dir = backend_dir / "recordings"
        
        print(f"\n[TRANSCRIPT] Searching for room: {room_name}")
        print(f"[TRANSCRIPT] Directory: {recordings_dir}")
        
        if not recordings_dir.exists():
            print(f"[TRANSCRIPT] ✗ Directory does not exist")
            return {
                "roomName": room_name,
                "hasTranscript": False,
                "message": f"Recordings directory not found: {recordings_dir}"
            }
        
        # List all files in this directory
        all_files = list(recordings_dir.glob("*.json"))
        print(f"[TRANSCRIPT] ✓ Found {len(all_files)} files")
        
        # Find the most recent file for this room
        matching_files = list(recordings_dir.glob(f"{room_name}_*.json"))
        if not matching_files:
            matching_files = [f for f in all_files if room_name in f.name]
        
        if not matching_files:
            print(f"[TRANSCRIPT] ✗ No files found for room {room_name}\n")
            return {
                "roomName": room_name,
                "hasTranscript": False,
                "message": f"No transcript found for room {room_name}"
            }
        
        # Get the most recent file
        latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
        print(f"[TRANSCRIPT] ✓ Using file: {latest_file.name}")
        
        # Read and return the transcript
        with open(latest_file, 'r') as f:
            transcript_data = json.load(f)
        
        messages = transcript_data.get("messages", [])
        print(f"[TRANSCRIPT] ✓ Loaded {len(messages)} messages")
        
        # Convert messages to UI format
        turns = []
        for idx, msg in enumerate(messages):
            # Determine speaker name
            speaker = msg["speaker"]
            if "dispatcher" in speaker.lower() or "tim" in speaker.lower():
                display_speaker = "Dispatcher"
            elif "driver" in speaker.lower() or "chris" in speaker.lower():
                display_speaker = "Driver"
            else:
                display_speaker = speaker
            
            turns.append({
                "speaker": display_speaker,
                "text": msg["message"],
                "timestamp": transcript_data.get("timestamp", "")
            })
            print(f"[TRANSCRIPT]   {idx + 1}. {display_speaker}: {msg['message'][:50]}")
        
        print(f"[TRANSCRIPT] ✓ Returning {len(turns)} turns\n")
        
        return {
            "roomName": room_name,
            "hasTranscript": True,
            "timestamp": transcript_data.get("timestamp"),
            "messageCount": len(turns),
            "turns": turns
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Error getting transcript:\n{error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transcript: {str(e)}"
        )


@router.get("/{room_name}/recording")
async def get_recording(room_name: str):
    """
    Get recording URL and transcript for a completed conversation.
    
    LiveKit automatically records rooms. This endpoint retrieves the recording information.
    """
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
        
        # List recordings for this room
        # Note: This API may vary - check LiveKit documentation
        try:
            # Try to get recordings (this depends on LiveKit version and setup)
            recordings = await lk_api.recording.list_recordings(
                room=room_name
            )
            await lk_api.aclose()
            
            return {
                "roomName": room_name,
                "recordingAvailable": len(recordings) > 0,
                "recordings": [
                    {
                        "id": r.id,
                        "status": str(r.status),
                        "location": r.location if hasattr(r, 'location') else None
                    }
                    for r in recordings
                ]
            }
        except AttributeError:
            # If recording API not available, return placeholder
            await lk_api.aclose()
            return {
                "roomName": room_name,
                "recordingAvailable": False,
                "message": "Recording functionality requires LiveKit Pro or Enterprise",
                "note": "Consider implementing client-side recording with MediaRecorder API"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error getting recording: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recording: {str(e)}"
        )


@router.post("/{room_name}/upload-audio")
async def upload_audio(room_name: str, audio: UploadFile = File(...)):
    """
    Upload audio recording for a completed conversation.
    
    This endpoint receives the MP3 audio file recorded by the frontend
    and saves it to the recordings/audio directory.
    """
    try:
        # Create audio recordings directory if it doesn't exist
        audio_dir = backend_dir / "recordings" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[AUDIO UPLOAD] Receiving audio for room: {room_name}")
        print(f"[AUDIO UPLOAD] File: {audio.filename}, Type: {audio.content_type}")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{room_name}_{timestamp}.mp3"
        filepath = audio_dir / filename
        
        # Save the uploaded file
        content = await audio.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        print(f"[AUDIO UPLOAD] ✓ Saved {file_size_mb:.2f}MB to {filepath}")
        
        return {
            "success": True,
            "roomName": room_name,
            "filename": filename,
            "fileSize": f"{file_size_mb:.2f}MB",
            "filepath": str(filepath)
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Error uploading audio:\n{error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload audio: {str(e)}"
        )


@router.get("/{room_name}/audio")
async def get_audio(room_name: str):
    """
    Get audio recording file for a completed conversation.
    
    Returns the MP3 audio file that was uploaded after the conversation.
    """
    try:
        audio_dir = backend_dir / "recordings" / "audio"
        
        print(f"\n[AUDIO FETCH] Searching for audio: {room_name}")
        print(f"[AUDIO FETCH] Directory: {audio_dir}")
        
        if not audio_dir.exists():
            print(f"[AUDIO FETCH] ✗ Directory does not exist")
            raise HTTPException(
                status_code=404,
                detail="Audio recordings directory not found"
            )
        
        # Find the most recent audio file for this room
        matching_files = list(audio_dir.glob(f"{room_name}_*.mp3"))
        
        if not matching_files:
            print(f"[AUDIO FETCH] ✗ No audio file found for room {room_name}")
            raise HTTPException(
                status_code=404,
                detail=f"No audio recording found for room {room_name}"
            )
        
        # Get the most recent file
        latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
        file_size_mb = latest_file.stat().st_size / (1024 * 1024)
        
        print(f"[AUDIO FETCH] ✓ Found: {latest_file.name} ({file_size_mb:.2f}MB)")
        
        # Return the file
        return FileResponse(
            path=str(latest_file),
            media_type="audio/mpeg",
            filename=latest_file.name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Error fetching audio:\n{error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audio: {str(e)}"
        )