# Corrected Architecture: Voice Agent Conversation System

## What This System Actually Does

Two AI voice agents (dispatcher and driver) join a LiveKit room and have a **real-time voice conversation** with each other. Users can observe the conversation through a web interface that connects to the same room via WebRTC.

## Architecture Overview

```
┌─────────────────────────┐
│   User Browser          │
│   (React + LiveKit SDK) │
│   - Observes room       │
│   - Hears conversation  │
└───────────┬─────────────┘
            │ WebRTC
            ↓
┌─────────────────────────┐
│   LiveKit Room          │
│   - Audio tracks        │
│   - Agent coordination  │
└───────────┬─────────────┘
            │
    ┌───────┴────────┐
    ↓                ↓
┌──────────┐    ┌──────────┐
│Dispatcher│    │ Driver   │
│  Agent   │ ←──→  Agent   │
│ Worker   │    │ Worker   │
└────┬─────┘    └─────┬────┘
     │                │
     └────────┬───────┘
              ↓
    ┌──────────────────┐
    │ OpenAI Realtime  │
    │      API         │
    │ (Voice/Audio)    │
    └──────────────────┘
```

## Key Components

### 1. LiveKit Server
- Manages WebRTC rooms
- Routes audio between participants
- Can be self-hosted or LiveKit Cloud

### 2. Dispatcher Agent (Python)
- LiveKit Agent Worker
- Uses OpenAI Realtime API for voice
- Joins room as "Dispatcher" participant
- Speaks first to initiate conversation
- Responds to driver's questions

### 3. Driver Agent (Python)
- LiveKit Agent Worker
- Uses OpenAI Realtime API for voice
- Joins room as "Driver" participant
- Responds to dispatcher
- Asks questions about the load

### 4. Frontend (React)
- Connects to LiveKit room as observer
- Uses LiveKit React SDK
- Displays audio visualizations
- Shows participant status
- Can display transcripts if available

## Technology Stack

### Backend
- **Python 3.10+**
- **LiveKit Agents SDK** (`livekit-agents`)
- **OpenAI Realtime API Plugin** (`livekit-plugins-openai`)
- **LiveKit Python SDK** (`livekit`)

### Frontend
- **React + TypeScript**
- **LiveKit React SDK** (`@livekit/components-react`)
- **LiveKit Client SDK** (`livekit-client`)

### External Services
- **LiveKit Cloud** or self-hosted LiveKit server
- **OpenAI API** (for Realtime API access)

## How It Works

### 1. Room Creation
```
User clicks "Generate Conversation"
  ↓
Backend creates LiveKit room
  ↓
Backend dispatches two agent jobs
  ↓
Dispatcher Agent joins room
Driver Agent joins room
```

### 2. Conversation Flow
```
Dispatcher Agent:
  - Receives scenario context
  - Uses OpenAI Realtime API
  - Speaks: "Hey Chris, it's Tim..."
  ↓ (audio via WebRTC)
Driver Agent:
  - Hears dispatcher via LiveKit room
  - OpenAI Realtime API processes audio
  - Responds: "Hey Tim, yeah go ahead"
  ↓ (continues back and forth)
```

### 3. User Observation
```
Frontend connects to room
  ↓
Subscribes to audio tracks
  ↓
Displays audio visualization
  ↓
Shows participant status
  ↓
User hears real-time conversation
```

## API Endpoints

### Backend API (FastAPI)

**POST /api/v1/conversations/create**
- Input: Scenario + Agent configs
- Creates LiveKit room
- Dispatches agents
- Returns: Room token for frontend

**GET /api/v1/conversations/{room_id}/status**
- Returns: Agent status, participant count

### Agent Workers

**Dispatcher Agent**
- Entrypoint: `dispatcher_agent.py`
- Connects to LiveKit server
- Waits for dispatch to room
- Uses OpenAI Realtime API

**Driver Agent**
- Entrypoint: `driver_agent.py`
- Connects to LiveKit server
- Waits for dispatch to room
- Uses OpenAI Realtime API

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Optional - Langfuse for observability
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_key
```

## Project Structure

```
dispatcher-agents/
├── backend/
│   ├── agents/
│   │   ├── dispatcher_agent.py    # Dispatcher worker
│   │   ├── driver_agent.py        # Driver worker
│   │   └── common.py              # Shared utilities
│   ├── api/
│   │   ├── main.py                # FastAPI app
│   │   └── routes/
│   │       └── rooms.py           # Room creation API
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConversationRoom.tsx  # LiveKit room component
│   │   │   ├── AudioVisualizer.tsx   # Audio viz
│   │   │   └── ScenarioForm.tsx      # Input form
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## Key Differences from Current Implementation

| Current (Wrong) | Correct |
|----------------|---------|
| Text-based LLM chat | Real-time voice conversation |
| OpenRouter API | OpenAI Realtime API |
| Sequential API calls | WebRTC audio streams |
| No real-time audio | Live audio via LiveKit |
| Transcript-only | Audio + optional transcripts |
| Single backend service | Agent workers + API server |
| No WebRTC | Full WebRTC support |

## Implementation Steps

1. **Setup LiveKit**
   - Create LiveKit Cloud account or self-host
   - Get API credentials

2. **Implement Agent Workers**
   - Create dispatcher agent with OpenAI Realtime
   - Create driver agent with OpenAI Realtime
   - Configure conversation prompts

3. **Implement Backend API**
   - Room creation endpoint
   - Agent dispatch logic
   - Token generation for frontend

4. **Implement Frontend**
   - LiveKit React components
   - Room connection
   - Audio visualization
   - Participant display

5. **Test End-to-End**
   - Create room
   - Agents join and converse
   - Frontend observes in real-time

## Benefits of Correct Architecture

✅ **Real-time**: Actual voice conversation happening live
✅ **Natural**: Proper turn-taking with VAD
✅ **Observable**: Users can hear conversation as it happens
✅ **Scalable**: LiveKit handles WebRTC complexity
✅ **Production-ready**: Built on proven LiveKit infrastructure
✅ **Multimodal**: Can add video, screen share, etc.

## Next Steps

1. Discard current text-based implementation
2. Implement LiveKit agent workers
3. Update frontend to use LiveKit React SDK
4. Test with OpenAI Realtime API

