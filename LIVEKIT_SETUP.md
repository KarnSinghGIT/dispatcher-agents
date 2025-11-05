# LiveKit Voice Agent Setup Guide

This is the **CORRECT** implementation using LiveKit Agents + OpenAI Realtime API for real-time voice conversations.

## Architecture

Two AI voice agents (Dispatcher and Driver) join a LiveKit room and have a **real-time audio conversation** via WebRTC. The frontend observes the conversation live.

```
User Browser → LiveKit Room ← Dispatcher Agent (OpenAI Realtime)
                    ↕
                Driver Agent (OpenAI Realtime)
```

## Prerequisites

### 1. LiveKit Account
- Sign up at [LiveKit Cloud](https://cloud.livekit.io)
- Or self-host LiveKit server
- Get your credentials:
  - `LIVEKIT_URL` (e.g., `wss://your-project.livekit.cloud`)
  - `LIVEKIT_API_KEY`
  - `LIVEKIT_API_SECRET`

### 2. OpenAI API Key
- Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- Must have access to **Realtime API** (gpt-4o-realtime-preview)

### 3. Software
- Python 3.10+
- Node.js 18+
- UV package manager: `pip install uv`

## Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
EOF
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

## Running the System

You need **4 terminals** to run the complete system:

### Terminal 1: Backend API Server

```bash
cd backend
source .venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

This starts the FastAPI server for room management.

### Terminal 2: Dispatcher Agent Worker

```bash
cd backend
source .venv/bin/activate
python agents/dispatcher_agent.py
```

This starts the dispatcher AI agent worker that will join rooms.

### Terminal 3: Driver Agent Worker

```bash
cd backend
source .venv/bin/activate
python agents/driver_agent.py
```

This starts the driver AI agent worker that will join rooms.

### Terminal 4: Frontend

```bash
cd frontend
npm run dev
```

Frontend will be at `http://localhost:5173`

## How to Use

1. **Open browser** to http://localhost:5173

2. **Configure the scenario**:
   - Load details are pre-filled (or customize them)
   - Agent prompts are pre-filled (or customize them)

3. **Click "Start Live Conversation"**:
   - Backend creates a LiveKit room
   - Frontend connects to room
   - Dispatcher agent joins room automatically
   - Driver agent joins room automatically

4. **Observe the conversation**:
   - Agents will talk to each other via WebRTC
   - You hear the conversation in real-time
   - See participant status (who's speaking)

5. **Listen**:
   - Dispatcher will greet and present the load
   - Driver will ask questions
   - They'll negotiate and complete the conversation
   - All happening live with real voices!

## Troubleshooting

### "Failed to create room"
- Check LiveKit credentials in backend `.env`
- Verify LiveKit server is accessible
- Check backend logs for details

### "Agents not joining"
- Make sure agent workers are running (Terminal 2 & 3)
- Check agent logs for errors
- Verify OPENAI_API_KEY is set
- Ensure you have access to OpenAI Realtime API

### "No audio"
- Check browser permissions (microphone/speaker)
- Verify WebRTC connection in browser console
- Check LiveKit room status

### "OpenAI Realtime API errors"
- Verify API key has Realtime API access
- Check OpenAI account credits/billing
- Review OpenAI API status page

## How It Actually Works

1. **Frontend calls Backend API** to create room
2. **Backend creates LiveKit room** with metadata (scenario, prompts)
3. **Backend returns room token** to frontend
4. **Frontend joins room** as observer (can subscribe, can't publish)
5. **Agent workers detect new room** and dispatch worker processes
6. **Dispatcher agent joins** room with OpenAI Realtime API
7. **Driver agent joins** room with OpenAI Realtime API
8. **Agents talk to each other** via WebRTC audio
9. **Frontend receives audio** and plays it in real-time

## Key Differences from Previous (Wrong) Implementation

| Old (Wrong) | New (Correct) |
|------------|---------------|
| Text-based LLM | Real voice conversation |
| OpenRouter API | OpenAI Realtime API |
| Sequential API calls | WebRTC audio streams |
| Generate transcript | Live audio conversation |
| No real-time | Actual real-time WebRTC |
| Single process | Distributed agent workers |

## API Endpoints

### POST /api/v1/rooms/create
Creates a LiveKit room for the conversation.

**Request:**
```json
{
  "scenario": { ... },
  "dispatcherAgent": { "role": "dispatcher", "prompt": "..." },
  "driverAgent": { "role": "driver", "prompt": "..." }
}
```

**Response:**
```json
{
  "roomName": "conv_HDX-2478_20250105_143022",
  "roomToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "livekitUrl": "wss://your-project.livekit.cloud",
  "conversationId": "conv_HDX-2478_20250105_143022"
}
```

### GET /api/v1/rooms/{room_name}/status
Get room status and participants.

## Architecture Components

### 1. Backend API (FastAPI)
- Creates and manages LiveKit rooms
- Generates tokens for frontend
- Stores scenario/agent configurations in room metadata

### 2. Dispatcher Agent Worker
- Python process using LiveKit Agents SDK
- Uses OpenAI Realtime API for voice
- Initiates conversation
- Presents load details

### 3. Driver Agent Worker
- Python process using LiveKit Agents SDK
- Uses OpenAI Realtime API for voice
- Responds to dispatcher
- Asks questions about the load

### 4. Frontend (React + LiveKit)
- Connects to LiveKit room
- Observes conversation in real-time
- Displays participant status
- Plays audio via WebRTC

## Files Changed/Created

### New Files:
- `backend/agents/dispatcher_agent.py` - Dispatcher worker
- `backend/agents/driver_agent.py` - Driver worker
- `backend/src/api/routes/rooms.py` - Room management API
- `frontend/src/components/ConversationRoom.tsx` - LiveKit room component
- `frontend/src/components/ConversationRoom.css` - Room styles
- `LIVEKIT_SETUP.md` - This file
- `CORRECTED_ARCHITECTURE.md` - Architecture overview

### Modified Files:
- `backend/pyproject.toml` - Updated dependencies
- `backend/src/api/main.py` - Use rooms router
- `frontend/package.json` - Added LiveKit packages
- `frontend/src/App.tsx` - Use LiveKit room
- `frontend/src/App.css` - New styles
- `frontend/src/services/api.ts` - Room API calls
- `frontend/src/types/index.ts` - Added RoomInfo type

### Deprecated Files (old implementation):
- `backend/src/services/llm_service.py` - Not used
- `backend/src/services/conversation_service.py` - Not used
- `backend/src/api/routes/conversations.py` - Replaced by rooms.py
- `frontend/src/components/TranscriptDisplay.tsx` - Not needed (live audio)
- `frontend/src/components/ConversationPlayer.tsx` - Not needed (live audio)

## Next Steps

1. **Test the system** with all 4 terminals running
2. **Customize agent prompts** for different scenarios
3. **Add features**:
   - Transcript recording (optional)
   - Conversation history
   - Multiple agent pairs
   - Video support
4. **Deploy**:
   - Backend to cloud server
   - Agent workers as separate services
   - Frontend to CDN

## Resources

- [LiveKit Documentation](https://docs.livekit.io)
- [LiveKit Agents Guide](https://docs.livekit.io/agents)
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [LiveKit React Components](https://docs.livekit.io/reference/components-react/)

## Support

For issues:
1. Check all 4 terminals for errors
2. Verify environment variables
3. Test LiveKit connection separately
4. Review OpenAI API logs

