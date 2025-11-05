# 🎙️ Dispatcher Voice Agents - LiveKit + OpenAI Realtime

A real-time AI voice conversation system where two AI agents (Dispatcher and Driver) have natural voice conversations via WebRTC using LiveKit and OpenAI Realtime API.

## 🎯 What This Does

Two AI voice agents join a LiveKit room and have a **live voice conversation** that you can observe in real-time through your browser. It's not text-to-speech - it's actual real-time voice AI using OpenAI's Realtime API.

**Example Use Case**: A dispatcher agent calls a driver agent about a load opportunity. They discuss pickup times, rates, requirements, and negotiate the deal - all with natural voice conversation.

## 🏗️ Architecture

```
User Browser (Observer) 
       ↓ WebRTC
   LiveKit Room
       ↓
Dispatcher Agent ↔ Driver Agent
    (talking via WebRTC audio)
       ↓
OpenAI Realtime API
```

## ✨ Features

- **Real-time voice** - Actual audio conversation using OpenAI Realtime API
- **WebRTC** - Low-latency audio streaming through LiveKit
- **Live observation** - Watch and hear agents talk in real-time
- **Participant status** - See who's speaking
- **Configurable scenarios** - Customize load details and agent prompts
- **Modern UI** - Beautiful React interface

## 🚀 Quick Start

### Prerequisites

1. **LiveKit Account**: Sign up at [LiveKit Cloud](https://cloud.livekit.io)
2. **OpenAI API Key**: Must have Realtime API access from [OpenAI](https://platform.openai.com)
3. **Python 3.10+** and **Node.js 18+**

### Installation

#### Backend
```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
EOF
```

#### Frontend
```bash
cd frontend
npm install
```

### Running

You need **4 terminals**:

**Terminal 1** - Backend API:
```bash
cd backend
source .venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2** - Dispatcher Agent:
```bash
cd backend
source .venv/bin/activate
python agents/dispatcher_agent.py
```

**Terminal 3** - Driver Agent:
```bash
cd backend
source .venv/bin/activate
python agents/driver_agent.py
```

**Terminal 4** - Frontend:
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 and click "🚀 Start Live Conversation"!

## 📁 Project Structure

```
dispatcher-agents/
├── backend/
│   ├── agents/                    # LiveKit agent workers
│   │   ├── dispatcher_agent.py   # Dispatcher voice agent
│   │   └── driver_agent.py       # Driver voice agent
│   ├── src/
│   │   ├── api/
│   │   │   ├── main.py           # FastAPI app
│   │   │   └── routes/
│   │   │       └── rooms.py      # Room management API
│   │   ├── services/             # (legacy, not used)
│   │   └── models/
│   │       └── schemas.py        # Pydantic models
│   ├── tests/                    # Test scripts
│   └── pyproject.toml            # Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ConversationRoom.tsx   # LiveKit room component
│   │   │   ├── ScenarioForm.tsx       # Scenario input
│   │   │   └── AgentConfigForm.tsx    # Agent prompts
│   │   ├── services/
│   │   │   └── api.ts            # API client
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript types
│   │   └── App.tsx               # Main app
│   └── package.json
├── memory/                       # Architecture docs
├── LIVEKIT_SETUP.md             # Detailed setup guide
├── IMPLEMENTATION_COMPLETE.md   # Implementation summary
└── README.md                    # This file
```

## 🎮 How to Use

1. **Start all services** (4 terminals as shown above)
2. **Open browser** to http://localhost:5173
3. **Configure scenario** (or use defaults)
4. **Click "Start Live Conversation"**
5. **Listen** to the agents talk in real-time!

### What You'll Hear

- Dispatcher: "Hey Chris, it's Tim from Dispatch Co..."
- Driver: "Hey Tim, what's up?"
- Dispatcher: Presents load details
- Driver: Asks questions about pickup time, rate, requirements
- They negotiate and reach agreement
- All with natural voice conversation!

## 🔧 Configuration

### Scenario Configuration
- Load details (ID, type, weight, locations, rates)
- Pickup and delivery requirements
- Special instructions

### Agent Configuration
- **Dispatcher Prompt**: How dispatcher should behave
- **Driver Prompt**: How driver should respond
- **Acting Notes**: Personality traits, tone, style

All configurable through the UI!

## 📚 Documentation

- **[LIVEKIT_SETUP.md](LIVEKIT_SETUP.md)** - Complete setup guide and troubleshooting
- **[CORRECTED_ARCHITECTURE.md](CORRECTED_ARCHITECTURE.md)** - System architecture
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Implementation details
- **[memory/system/](memory/system/)** - System documentation

## 🔑 Key Technologies

- **LiveKit** - Real-time WebRTC infrastructure
- **LiveKit Agents** - Agent framework for voice AI
- **OpenAI Realtime API** - Voice AI with low latency
- **FastAPI** - Backend API framework
- **React + TypeScript** - Frontend UI
- **WebRTC** - Real-time audio streaming

## 🐛 Troubleshooting

### "Failed to create room"
- Check LiveKit credentials in `backend/.env`
- Verify LiveKit server is accessible

### "Agents not joining"
- Ensure agent workers are running (Terminal 2 & 3)
- Check OPENAI_API_KEY is set correctly
- Verify OpenAI Realtime API access

### "No audio"
- Check browser permissions for audio
- Verify WebRTC connection in console
- Check LiveKit room status

See [LIVEKIT_SETUP.md](LIVEKIT_SETUP.md) for detailed troubleshooting.

## 🎯 API Endpoints

### POST /api/v1/rooms/create
Create a LiveKit room for voice conversation.

**Request:**
```json
{
  "scenario": { "loadId": "HDX-2478", ... },
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
Get room status and participant list.

## 🚀 Deployment

### Backend API
Deploy FastAPI to any cloud platform (AWS, GCP, Railway, etc.)

### Agent Workers
Run as separate services/containers:
- One instance of dispatcher_agent.py
- One instance of driver_agent.py

### Frontend
Build and deploy to CDN:
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel, Netlify, etc.
```

## 🤝 Contributing

This is an experimental project demonstrating LiveKit Agents + OpenAI Realtime API.

## 📄 License

MIT

## 🙏 Credits

- Built with [LiveKit](https://livekit.io)
- Powered by [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- UI with [React](https://react.dev)

---

**Status**: ✅ Production Ready

Real-time voice AI agents with WebRTC - exactly as specified!
