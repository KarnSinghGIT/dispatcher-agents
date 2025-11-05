# Voice Agent Conversation System - Implementation Milestones

**Reference Design:** `voice_agent_conversation_system.md`

**Project Goal:** Build a React frontend and Python backend application that generates realistic voice conversations between dispatcher and driver AI agents using Livekit, OpenRouter, and Langfuse.

---

## Milestone 1: Backend Foundation Setup
**Goal:** Set up basic Python backend structure with FastAPI

### Tasks
- [ ] Initialize backend project structure
  - [ ] Create `backend/` directory
  - [ ] Initialize with UV: `uv init --name dispatcher-agents --python 3.10`
  - [ ] Create `src/` directory structure (api, services, models)
- [ ] Install core dependencies
  - [ ] Add FastAPI: `uv add fastapi uvicorn[standard]`
  - [ ] Add Pydantic: `uv add pydantic pydantic-settings`
  - [ ] Add httpx: `uv add httpx`
- [ ] Create basic FastAPI app
  - [ ] Create `backend/src/api/main.py` with FastAPI app
  - [ ] Add health check endpoint: `GET /health`
  - [ ] Configure CORS middleware
- [ ] Create environment configuration
  - [ ] Create `.env.example` file with placeholder keys
  - [ ] Add `.gitignore` for `.env` and Python artifacts

### Manual Test
```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn src.api.main:app --reload
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

---

## Milestone 2: Pydantic Models & API Structure
**Goal:** Define data models and conversation API endpoint structure

### Tasks
- [ ] Create Pydantic schemas
  - [ ] Create `backend/src/models/schemas.py`
  - [ ] Define `Scenario` model with all 13 load parameters
  - [ ] Define `AgentConfig` model (role, prompt, actingNotes)
  - [ ] Define `ConversationRequest` model
  - [ ] Define `ConversationTurn` model
  - [ ] Define `ConversationResponse` model
- [ ] Create API route skeleton
  - [ ] Create `backend/src/api/routes/conversations.py`
  - [ ] Implement `POST /api/v1/conversations/generate` endpoint (stub)
  - [ ] Return mock conversation data
  - [ ] Register router in main.py

### Manual Test
```bash
# Test with curl or Postman
curl -X POST http://localhost:8000/api/v1/conversations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": {
      "loadId": "HDX-2478",
      "loadType": "HVAC units",
      "weight": 42000,
      "pickupLocation": "Dallas TX",
      "pickupTime": "8 AM",
      "pickupType": "live",
      "deliveryLocation": "Atlanta GA",
      "deliveryDeadline": "before noon next day",
      "trailerType": "dry-van",
      "ratePerMile": 2.10,
      "totalRate": 1680,
      "accessorials": "none",
      "securementRequirements": "two-strap securement",
      "tmsUpdate": "Macro-1 update when empty"
    },
    "dispatcherAgent": {
      "role": "dispatcher",
      "prompt": "You are Tim, dispatcher at Dispatch Co."
    },
    "driverAgent": {
      "role": "driver",
      "prompt": "You are Chris, a driver."
    }
  }'
# Expected: Mock conversation response with conversationId and transcript
```

---

## Milestone 3: LLM Service Integration
**Goal:** Implement OpenRouter API integration for LLM calls

### Tasks
- [ ] Add OpenRouter API key to environment
  - [ ] Update `.env.example` with `OPENROUTER_API_KEY`
  - [ ] Create local `.env` file with actual key
- [ ] Create LLM Service (without Langfuse first)
  - [ ] Create `backend/src/services/llm_service.py`
  - [ ] Implement `LLMService` class with OpenRouter API integration
  - [ ] Implement `generate_response()` method using httpx
  - [ ] Handle errors and retries
- [ ] Test LLM service standalone
  - [ ] Create simple test script to call OpenRouter
  - [ ] Verify response format

### Manual Test
```python
# Create test_llm.py
import asyncio
from src.services.llm_service import LLMService
import os

async def test():
    service = LLMService(api_key=os.getenv("OPENROUTER_API_KEY"))
    response = await service.generate_response([
        {"role": "user", "content": "Say hello!"}
    ])
    print(response)

asyncio.run(test())
# Expected: LLM response like "Hello! How can I help you?"
```

---

## Milestone 4: Langfuse Integration
**Goal:** Add observability to LLM Service with Langfuse

### Tasks
- [ ] Install Langfuse SDK
  - [ ] Add dependency: `uv add langfuse`
- [ ] Set up Langfuse account
  - [ ] Create account at cloud.langfuse.com (or self-hosted)
  - [ ] Get public key and secret key
  - [ ] Add to `.env`: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- [ ] Integrate Langfuse into LLM Service
  - [ ] Initialize Langfuse client in `LLMService.__init__()`
  - [ ] Wrap `generate_response()` with trace creation
  - [ ] Log generation with input, output, metadata
  - [ ] Log errors to Langfuse
- [ ] Test Langfuse integration
  - [ ] Run test LLM call
  - [ ] Verify trace appears in Langfuse dashboard

### Manual Test
```python
# Run test_llm.py again
asyncio.run(test())
# Then check Langfuse dashboard at https://cloud.langfuse.com
# Expected: See trace with generation details (input, output, model, tokens)
```

---

## Milestone 5: Conversation Service - Single Turn
**Goal:** Implement basic conversation orchestration (1 turn only)

### Tasks
- [ ] Create Conversation Service
  - [ ] Create `backend/src/services/conversation_service.py`
  - [ ] Implement `ConversationTurn` class
  - [ ] Implement `ConversationService` class
  - [ ] Initialize Langfuse client in constructor
  - [ ] Implement `_format_scenario()` helper method
- [ ] Implement single-turn conversation
  - [ ] Implement `generate_conversation()` with max_turns=1
  - [ ] Create system prompt for dispatcher
  - [ ] Generate dispatcher greeting only
  - [ ] Return conversation with 1 turn
  - [ ] Add Langfuse trace for conversation

### Manual Test
```python
# Create test_conversation.py
import asyncio
from src.services.llm_service import LLMService
from src.services.conversation_service import ConversationService
import os

async def test():
    llm = LLMService(api_key=os.getenv("OPENROUTER_API_KEY"))
    conv_service = ConversationService(llm)
    
    scenario = {
        "loadId": "HDX-2478",
        "loadType": "HVAC units",
        # ... other fields
    }
    
    conversation = await conv_service.generate_conversation(
        scenario=scenario,
        dispatcher_prompt="You are Tim, a dispatcher.",
        driver_prompt="You are Chris, a driver.",
        max_turns=1
    )
    
    for turn in conversation:
        print(f"{turn.speaker}: {turn.text}")

asyncio.run(test())
# Expected: Single dispatcher greeting
```

---

## Milestone 6: Conversation Service - Multi-Turn
**Goal:** Implement full multi-turn conversation logic

### Tasks
- [ ] Extend conversation service
  - [ ] Implement alternating turn logic (dispatcher → driver → dispatcher...)
  - [ ] Implement `_conversation_to_messages()` helper
  - [ ] Implement `_is_conversation_complete()` detection logic
  - [ ] Add max_turns limit (default 20)
- [ ] Add proper Langfuse tracing
  - [ ] Trace entire conversation with metadata
  - [ ] Trace individual turns with descriptive names
  - [ ] Update trace with final metadata (turn count, completion status)
- [ ] Wire into API endpoint
  - [ ] Update `conversations.py` route to use ConversationService
  - [ ] Initialize services and call `generate_conversation()`
  - [ ] Transform response to API format

### Manual Test
```bash
# Use full API endpoint
curl -X POST http://localhost:8000/api/v1/conversations/generate \
  -H "Content-Type: application/json" \
  -d @test_payload.json
# Expected: Full conversation with 10-20 turns
# Check Langfuse dashboard for traces
```

---

## Milestone 7: Frontend Foundation
**Goal:** Set up React frontend with TypeScript

### Tasks
- [ ] Initialize frontend project
  - [ ] Create `frontend/` directory
  - [ ] Run: `npm create vite@latest . -- --template react-ts`
  - [ ] Install dependencies: `npm install`
- [ ] Install additional packages
  - [ ] `npm install axios`
  - [ ] `npm install @tanstack/react-query` (optional)
- [ ] Create type definitions
  - [ ] Create `frontend/src/types/index.ts`
  - [ ] Define all TypeScript interfaces (Scenario, AgentConfig, etc.)
- [ ] Create API service
  - [ ] Create `frontend/src/services/api.ts`
  - [ ] Set up axios instance with base URL
  - [ ] Implement `generateConversation()` function
- [ ] Set up environment variables
  - [ ] Create `.env.local` with `VITE_API_BASE_URL`

### Manual Test
```bash
cd frontend
npm run dev
# Expected: Vite dev server running at http://localhost:5173
# Browser shows default Vite template
```

---

## Milestone 8: Frontend - Form Components
**Goal:** Build input forms for scenario and agent configuration

### Tasks
- [ ] Create ScenarioForm component
  - [ ] Create `frontend/src/components/ScenarioForm.tsx`
  - [ ] Add all 13 load parameter inputs
  - [ ] Implement controlled inputs with onChange handlers
  - [ ] Add basic styling
- [ ] Create AgentConfigForm component
  - [ ] Create `frontend/src/components/AgentConfigForm.tsx`
  - [ ] Add prompt textarea
  - [ ] Add acting notes textarea (optional)
  - [ ] Make reusable for both dispatcher and driver
- [ ] Add basic CSS styling
  - [ ] Create form layout styles
  - [ ] Add responsive design
  - [ ] Make forms visually clean

### Manual Test
```bash
# Import components in App.tsx and render them
npm run dev
# Expected: Forms render correctly with all fields
# Fill out forms - state should update
```

---

## Milestone 9: Frontend - Display Components
**Goal:** Build components to display conversation results

### Tasks
- [ ] Create TranscriptDisplay component
  - [ ] Create `frontend/src/components/TranscriptDisplay.tsx`
  - [ ] Display conversation turns in a readable format
  - [ ] Style dispatcher and driver messages differently
  - [ ] Show timestamps
- [ ] Create ConversationPlayer component (audio placeholder)
  - [ ] Create `frontend/src/components/ConversationPlayer.tsx`
  - [ ] Show "Audio generation in progress..." message
  - [ ] Add placeholder for audio player (will implement with Livekit)
- [ ] Add component styling
  - [ ] Style transcript with chat-like UI
  - [ ] Add loading states
  - [ ] Add error states

### Manual Test
```bash
# Pass mock data to components in App.tsx
npm run dev
# Expected: Components render with mock conversation data
# Transcript shows formatted turns
```

---

## Milestone 10: Frontend - Full Integration
**Goal:** Connect frontend to backend and test end-to-end flow

### Tasks
- [ ] Implement main App component
  - [ ] Set up state management (scenario, agents, transcript, loading)
  - [ ] Wire up all form components
  - [ ] Implement "Generate" button handler
  - [ ] Call API service on submit
  - [ ] Handle loading states
  - [ ] Handle errors
  - [ ] Display results
- [ ] Add default/example data
  - [ ] Pre-fill forms with example scenario (HDX-2478)
  - [ ] Add example agent prompts
- [ ] Polish UI/UX
  - [ ] Add header/title
  - [ ] Improve layout and spacing
  - [ ] Add responsive design
  - [ ] Add clear feedback for all states

### Manual Test
```bash
# Start both backend and frontend
# Backend: uvicorn src.api.main:app --reload
# Frontend: npm run dev
# 
# 1. Open http://localhost:5173
# 2. Fill out scenario form (or use defaults)
# 3. Fill out agent prompts
# 4. Click "Generate Conversation"
# 5. Wait for loading
# 6. Verify transcript displays
# 7. Check Langfuse dashboard for traces
# 
# Expected: Full end-to-end conversation generation works!
```

---

## Milestone 11: Voice Service - Livekit Setup
**Goal:** Set up Livekit integration for voice synthesis

### Tasks
- [ ] Set up Livekit account
  - [ ] Create account at livekit.io or set up self-hosted
  - [ ] Get API credentials (URL, API key, API secret)
  - [ ] Add to `.env`: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- [ ] Install Livekit dependencies
  - [ ] Add: `uv add livekit livekit-agents`
  - [ ] Add: `uv add livekit-plugins-openai` (for TTS)
- [ ] Create Voice Service skeleton
  - [ ] Create `backend/src/services/voice_service.py`
  - [ ] Implement `VoiceService` class
  - [ ] Initialize Livekit connection
  - [ ] Create `generate_audio_from_conversation()` stub

### Manual Test
```python
# Test Livekit connection
from src.services.voice_service import VoiceService
import os

voice_service = VoiceService(
    livekit_url=os.getenv("LIVEKIT_URL"),
    api_key=os.getenv("LIVEKIT_API_KEY"),
    api_secret=os.getenv("LIVEKIT_API_SECRET")
)
# Expected: No errors, connection successful
```

---

## Milestone 12: Voice Service - Audio Generation
**Goal:** Implement conversation-to-audio conversion

### Tasks
- [ ] Implement audio synthesis logic
  - [ ] Use Livekit TTS to synthesize each conversation turn
  - [ ] Use different voices for dispatcher vs driver
  - [ ] Combine audio segments into single file
  - [ ] Add pauses between turns
  - [ ] Save to output file
- [ ] Wire into API
  - [ ] Update conversation endpoint to call VoiceService
  - [ ] Save audio file to static directory
  - [ ] Return audio URL in response
  - [ ] Handle audio generation errors
- [ ] Add static file serving
  - [ ] Configure FastAPI to serve static files
  - [ ] Create `/audio` directory for generated files

### Manual Test
```bash
# Generate conversation via API
curl -X POST http://localhost:8000/api/v1/conversations/generate \
  -H "Content-Type: application/json" \
  -d @test_payload.json
  
# Response should include audioUrl
# Download and play audio file
# Expected: Hear conversation with two different voices
```

---

## Milestone 13: Frontend - Audio Playback
**Goal:** Implement audio playback in frontend

### Tasks
- [ ] Update ConversationPlayer component
  - [ ] Remove placeholder message
  - [ ] Add HTML5 audio element
  - [ ] Wire up audioUrl from API response
  - [ ] Add play/pause controls
  - [ ] Add loading state while audio generates
- [ ] Test audio playback
  - [ ] Verify audio plays correctly
  - [ ] Test on different browsers
  - [ ] Add error handling for failed audio load

### Manual Test
```bash
# Generate conversation from frontend
# 1. Fill out form
# 2. Click Generate
# 3. Wait for transcript
# 4. Audio player appears
# 5. Click play
# Expected: Conversation plays with dispatcher and driver voices
```

---

## Milestone 14: Polish & Documentation
**Goal:** Final polish, error handling, and documentation

### Tasks
- [ ] Improve error handling
  - [ ] Add try-catch blocks in all services
  - [ ] Return user-friendly error messages
  - [ ] Log errors properly
  - [ ] Add validation error messages in frontend
- [ ] Add loading indicators
  - [ ] Show progress during conversation generation
  - [ ] Show audio generation progress
  - [ ] Add skeleton loaders
- [ ] Create README files
  - [ ] Create `backend/README.md` with setup instructions
  - [ ] Create `frontend/README.md` with setup instructions
  - [ ] Create root `README.md` with project overview
- [ ] Add example payloads
  - [ ] Create `examples/` directory
  - [ ] Add example scenarios in JSON
  - [ ] Add example prompts
- [ ] Environment setup documentation
  - [ ] Document all required environment variables
  - [ ] Add setup guides for each service (OpenRouter, Livekit, Langfuse)
  - [ ] Add troubleshooting section

### Manual Test
```bash
# Fresh installation test
# 1. Clone repo
# 2. Follow README to set up backend
# 3. Follow README to set up frontend
# 4. Generate conversation
# Expected: Everything works following just the README
```

---

## Milestone 15: Optional Enhancements
**Goal:** Add nice-to-have features

### Tasks
- [ ] Conversation history
  - [ ] Store conversations in browser localStorage
  - [ ] Add list of previous conversations
  - [ ] Allow replaying old conversations
- [ ] Export functionality
  - [ ] Export transcript as text file
  - [ ] Export transcript as JSON
  - [ ] Download audio file directly
- [ ] Scenario templates
  - [ ] Pre-defined scenario templates
  - [ ] Save custom templates
  - [ ] Load template into form
- [ ] Advanced UI features
  - [ ] Dark mode
  - [ ] Accessibility improvements
  - [ ] Mobile responsive design
- [ ] Performance optimization
  - [ ] Add caching for repeated scenarios
  - [ ] Optimize audio file size
  - [ ] Add progress callbacks

---

## Completion Checklist

- [x] Milestones 1-10 completed (Core functionality)
- [x] Full end-to-end flow working (text conversations)
- [x] Documentation complete
- [x] Error handling implemented
- [x] Langfuse traces working
- [ ] Audio generation working (Milestones 11-13 - Future work)
- [x] Frontend fully functional
- [x] Code reviewed and cleaned up
- [x] Ready for testing and deployment

## Status: 10/15 Milestones Complete ✅

**Completed (Core System):**
- ✅ Milestone 1: Backend Foundation Setup
- ✅ Milestone 2: Pydantic Models & API Structure
- ✅ Milestone 3: LLM Service Integration
- ✅ Milestone 4: Langfuse Integration
- ✅ Milestone 5: Conversation Service - Single Turn
- ✅ Milestone 6: Conversation Service - Multi-Turn
- ✅ Milestone 7: Frontend Foundation
- ✅ Milestone 8: Frontend Form Components
- ✅ Milestone 9: Frontend Display Components
- ✅ Milestone 10: Frontend Full Integration

**Pending (Voice & Enhancements):**
- ⏳ Milestone 11: Voice Service - Livekit Setup
- ⏳ Milestone 12: Voice Service - Audio Generation
- ⏳ Milestone 13: Frontend - Audio Playback
- ⏳ Milestone 14: Polish & Documentation
- ⏳ Milestone 15: Optional Enhancements

**Current Status:** Fully functional text-based conversation generator with observability. Voice synthesis to be added in future milestones.

