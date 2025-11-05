# Voice Agent Conversation System

## Overview

This document describes the architecture and implementation plan for a React frontend and Python backend application that generates realistic voice conversations between two AI agents (a dispatcher and a driver) using Livekit for voice synthesis, OpenRouter for LLM capabilities, and Langfuse for observability and tracing.

## System Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Input Forms)  │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  Python Backend │
│   (FastAPI)     │
└────────┬────────┘
         │
         ├─► OpenRouter API (LLM)
         ├─► Livekit (Voice/TTS)
         └─► Langfuse (Observability & Tracing)
```

## Tech Stack

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Modern CSS or Tailwind** - Styling
- **Axios/Fetch** - API calls
- **Web Audio API** - Audio playback

### Backend
- **Python 3.10+** - Runtime
- **UV** - Package manager
- **FastAPI** - Web framework
- **Livekit** - Voice agent framework
- **OpenRouter API** - LLM provider
- **Langfuse** - LLM observability and tracing (required)

### External Services
- **OpenRouter API** - For LLM calls (GPT-4, Claude, etc.)
- **Livekit** - For voice synthesis and real-time audio
- **Langfuse** - For conversation tracking, analytics, and LLM observability (required)

## Project Structure

```
dispatcher-agents/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ScenarioForm.tsx
│   │   │   ├── AgentConfigForm.tsx
│   │   │   ├── ConversationPlayer.tsx
│   │   │   └── TranscriptDisplay.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── conversations.py
│   │   │   └── main.py
│   │   ├── agents/
│   │   │   ├── dispatcher_agent.py
│   │   │   └── driver_agent.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── voice_service.py
│   │   │   └── conversation_service.py
│   │   └── models/
│   │       └── schemas.py
│   ├── pyproject.toml
│   └── README.md
├── .env.example
└── README.md
```

## Input Schema

### Scenario Description
```typescript
interface Scenario {
  loadId: string;                    // e.g., "HDX-2478"
  loadType: string;                  // e.g., "HVAC units"
  weight: number;                    // e.g., 42000 (lbs)
  pickupLocation: string;            // e.g., "Dallas TX"
  pickupTime: string;                // e.g., "8 AM"
  pickupType: string;                // e.g., "live"
  deliveryLocation: string;          // e.g., "Atlanta GA"
  deliveryDeadline: string;           // e.g., "before noon next day"
  trailerType: string;               // e.g., "dry-van"
  ratePerMile: number;               // e.g., 2.10
  totalRate: number;                 // e.g., 1680
  accessorials: string;              // e.g., "none"
  securementRequirements: string;    // e.g., "two-strap securement"
  tmsUpdate: string;                 // e.g., "Macro-1 update when empty"
}
```

### Agent Configuration
```typescript
interface AgentConfig {
  role: 'dispatcher' | 'driver';
  prompt: string;
  actingNotes?: string;
}

interface ConversationRequest {
  scenario: Scenario;
  dispatcherAgent: AgentConfig;
  driverAgent: AgentConfig;
}
```

## Backend Implementation

### 1. Setup with UV

```bash
# Install UV
pip install uv

# Initialize project
cd backend
uv init --name dispatcher-agents --python 3.10

# Add dependencies
uv add fastapi uvicorn[standard]
uv add livekit livekit-agents
uv add openai
uv add pydantic pydantic-settings
uv add httpx
uv add langfuse
```

### 2. Environment Variables (.env)

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
LIVEKIT_URL=wss://your-livekit-instance.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Core Services

#### LLM Service (`backend/src/services/llm_service.py`)

```python
import httpx
from typing import List, Dict
from langfuse import Langfuse
from langfuse.decorators import langfuse_context
import os

class LLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/yourusername/dispatcher-agents",
            "X-Title": "Dispatcher Agents"
        }
        # Initialize Langfuse for observability
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4o",
        temperature: float = 0.7,
        trace_name: str = "llm_call"
    ) -> str:
        # Create Langfuse trace for observability
        trace = self.langfuse.trace(name=trace_name)
        generation = trace.generation(
            name="openrouter_chat",
            model=model,
            input=messages,
            metadata={"temperature": temperature}
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Log the response to Langfuse
                generation.end(
                    output=content,
                    metadata={
                        "usage": data.get("usage", {}),
                        "model": model
                    }
                )
                
                return content
        except Exception as e:
            # Log error to Langfuse
            generation.end(
                output=None,
                level="ERROR",
                status_message=str(e)
            )
            raise
```

#### Conversation Service (`backend/src/services/conversation_service.py`)

```python
from typing import List, Dict
from datetime import datetime
from .llm_service import LLMService

class ConversationTurn:
    def __init__(self, speaker: str, text: str):
        self.speaker = speaker
        self.text = text
        self.timestamp = datetime.now()

class ConversationService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        from langfuse import Langfuse
        import os
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
    
    async def generate_conversation(
        self,
        scenario: Dict,
        dispatcher_prompt: str,
        driver_prompt: str,
        max_turns: int = 20
    ) -> List[ConversationTurn]:
        # Create Langfuse trace for the entire conversation
        trace = self.langfuse.trace(
            name="conversation_generation",
            metadata={
                "scenario": scenario.get("loadId"),
                "max_turns": max_turns
            }
        )
        conversation = []
        
        # Initialize system prompts
        dispatcher_system = f"""{dispatcher_prompt}

You are having a phone conversation with a driver about a load assignment.
Scenario: {self._format_scenario(scenario)}

Keep responses natural, brief, and conversational. Don't include stage directions.
"""
        
        driver_system = f"""{driver_prompt}

You are having a phone conversation with a dispatcher about a load assignment.
Scenario: {self._format_scenario(scenario)}

Keep responses natural, brief, and conversational. Don't include stage directions.
"""
        
        # Start conversation
        dispatcher_message = await self.llm_service.generate_response(
            [
                {"role": "system", "content": dispatcher_system},
                {"role": "user", "content": "Start the conversation with a greeting."}
            ],
            trace_name="dispatcher_opening"
        )
        
        conversation.append(ConversationTurn("Dispatcher", dispatcher_message))
        
        # Generate turns
        messages = [
            {"role": "system", "content": dispatcher_system},
            {"role": "assistant", "content": dispatcher_message}
        ]
        
        for turn_num in range(max_turns):
            # Driver responds
            driver_messages = [
                {"role": "system", "content": driver_system}
            ] + self._conversation_to_messages(conversation, "Driver")
            
            driver_response = await self.llm_service.generate_response(
                driver_messages,
                trace_name=f"driver_turn_{turn_num}"
            )
            conversation.append(ConversationTurn("Driver", driver_response))
            
            # Check for conversation end
            if self._is_conversation_complete(driver_response):
                break
            
            # Dispatcher responds
            messages.append({"role": "user", "content": driver_response})
            dispatcher_response = await self.llm_service.generate_response(
                messages,
                trace_name=f"dispatcher_turn_{turn_num}"
            )
            conversation.append(ConversationTurn("Dispatcher", dispatcher_response))
            messages.append({"role": "assistant", "content": dispatcher_response})
            
            if self._is_conversation_complete(dispatcher_response):
                break
        
        # End the trace with final conversation metadata
        trace.update(
            metadata={
                "total_turns": len(conversation),
                "completed": True
            }
        )
        
        return conversation
    
    def _format_scenario(self, scenario: Dict) -> str:
        return f"""
Load ID: {scenario['loadId']}
Load Type: {scenario['loadType']}
Weight: {scenario['weight']} lbs
Pickup: {scenario['pickupLocation']} at {scenario['pickupTime']} ({scenario['pickupType']})
Delivery: {scenario['deliveryLocation']} by {scenario['deliveryDeadline']}
Trailer: {scenario['trailerType']}
Rate: ${scenario['ratePerMile']}/mile (${scenario['totalRate']} total)
Accessorials: {scenario['accessorials']}
Securement: {scenario['securementRequirements']}
TMS Update: {scenario['tmsUpdate']}
"""
    
    def _conversation_to_messages(self, conversation: List[ConversationTurn], speaker: str) -> List[Dict]:
        messages = []
        for turn in conversation:
            role = "assistant" if turn.speaker == speaker else "user"
            messages.append({"role": role, "content": turn.text})
        return messages
    
    def _is_conversation_complete(self, text: str) -> bool:
        # Simple heuristic - can be improved
        end_phrases = [
            "thanks",
            "talk soon",
            "have a good one",
            "see you",
            "bye"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in end_phrases)
```

#### Voice Service (`backend/src/services/voice_service.py`)

```python
from livekit import agents, rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
    voice,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, silero
import asyncio
from typing import List
from .conversation_service import ConversationTurn

class VoiceService:
    def __init__(self, livekit_url: str, api_key: str, api_secret: str):
        self.livekit_url = livekit_url
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def generate_audio_from_conversation(
        self,
        conversation: List[ConversationTurn],
        output_path: str
    ) -> str:
        """
        Generate audio file from conversation turns using Livekit TTS.
        """
        # Use Livekit's voice synthesis
        # This is a simplified version - actual implementation will use Livekit agents
        
        # For now, use a TTS service compatible with Livekit
        # You'll need to integrate with Livekit's voice synthesis APIs
        
        # Pseudocode:
        # 1. For each turn in conversation:
        #    - Synthesize audio for the speaker's text
        #    - Combine into single audio file
        # 2. Save to output_path
        
        # Note: Full Livekit integration requires setting up agents properly
        # See Livekit documentation for detailed implementation
        
        pass
```

### 4. API Routes (`backend/src/api/routes/conversations.py`)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ...services.conversation_service import ConversationService
from ...services.llm_service import LLMService
from ...services.voice_service import VoiceService

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

class Scenario(BaseModel):
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
    role: str
    prompt: str
    actingNotes: Optional[str] = None

class ConversationRequest(BaseModel):
    scenario: Scenario
    dispatcherAgent: AgentConfig
    driverAgent: AgentConfig

class ConversationTurn(BaseModel):
    speaker: str
    text: str
    timestamp: str

class ConversationResponse(BaseModel):
    conversationId: str
    transcript: List[ConversationTurn]
    audioUrl: Optional[str] = None

@router.post("/generate", response_model=ConversationResponse)
async def generate_conversation(request: ConversationRequest):
    try:
        # Initialize services
        llm_service = LLMService(api_key=os.getenv("OPENROUTER_API_KEY"))
        conversation_service = ConversationService(llm_service)
        
        # Generate conversation
        conversation_turns = await conversation_service.generate_conversation(
            scenario=request.scenario.dict(),
            dispatcher_prompt=request.dispatcherAgent.prompt,
            driver_prompt=request.driverAgent.prompt
        )
        
        # Convert to response format
        transcript = [
            ConversationTurn(
                speaker=turn.speaker,
                text=turn.text,
                timestamp=turn.timestamp.isoformat()
            )
            for turn in conversation_turns
        ]
        
        # Generate audio (async, can be background task)
        # audio_url = await voice_service.generate_audio(...)
        
        return ConversationResponse(
            conversationId=datetime.now().isoformat(),
            transcript=transcript,
            audioUrl=None  # Will be populated when audio is ready
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5. Main Application (`backend/src/api/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import conversations

app = FastAPI(title="Dispatcher Agents API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Frontend Implementation

### 1. Setup

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install axios
npm install @tanstack/react-query  # Optional, for better data fetching
```

### 2. Types (`frontend/src/types/index.ts`)

```typescript
export interface Scenario {
  loadId: string;
  loadType: string;
  weight: number;
  pickupLocation: string;
  pickupTime: string;
  pickupType: string;
  deliveryLocation: string;
  deliveryDeadline: string;
  trailerType: string;
  ratePerMile: number;
  totalRate: number;
  accessorials: string;
  securementRequirements: string;
  tmsUpdate: string;
}

export interface AgentConfig {
  role: 'dispatcher' | 'driver';
  prompt: string;
  actingNotes?: string;
}

export interface ConversationRequest {
  scenario: Scenario;
  dispatcherAgent: AgentConfig;
  driverAgent: AgentConfig;
}

export interface ConversationTurn {
  speaker: string;
  text: string;
  timestamp: string;
}

export interface ConversationResponse {
  conversationId: string;
  transcript: ConversationTurn[];
  audioUrl?: string;
}
```

### 3. API Service (`frontend/src/services/api.ts`)

```typescript
import axios from 'axios';
import type { ConversationRequest, ConversationResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const generateConversation = async (
  request: ConversationRequest
): Promise<ConversationResponse> => {
  const response = await api.post<ConversationResponse>(
    '/api/v1/conversations/generate',
    request
  );
  return response.data;
};
```

### 4. Components

#### ScenarioForm (`frontend/src/components/ScenarioForm.tsx`)

```typescript
import React from 'react';
import type { Scenario } from '../types';

interface ScenarioFormProps {
  scenario: Scenario;
  onChange: (scenario: Scenario) => void;
}

export const ScenarioForm: React.FC<ScenarioFormProps> = ({ scenario, onChange }) => {
  const handleChange = (field: keyof Scenario, value: string | number) => {
    onChange({ ...scenario, [field]: value });
  };

  return (
    <div className="scenario-form">
      <h2>Load Scenario</h2>
      
      <div className="form-group">
        <label>Load ID</label>
        <input
          type="text"
          value={scenario.loadId}
          onChange={(e) => handleChange('loadId', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Load Type</label>
        <input
          type="text"
          value={scenario.loadType}
          onChange={(e) => handleChange('loadType', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Weight (lbs)</label>
        <input
          type="number"
          value={scenario.weight}
          onChange={(e) => handleChange('weight', parseInt(e.target.value))}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Pickup Location</label>
          <input
            type="text"
            value={scenario.pickupLocation}
            onChange={(e) => handleChange('pickupLocation', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Pickup Time</label>
          <input
            type="text"
            value={scenario.pickupTime}
            onChange={(e) => handleChange('pickupTime', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Pickup Type</label>
          <input
            type="text"
            value={scenario.pickupType}
            onChange={(e) => handleChange('pickupType', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Delivery Location</label>
          <input
            type="text"
            value={scenario.deliveryLocation}
            onChange={(e) => handleChange('deliveryLocation', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Delivery Deadline</label>
          <input
            type="text"
            value={scenario.deliveryDeadline}
            onChange={(e) => handleChange('deliveryDeadline', e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Trailer Type</label>
        <input
          type="text"
          value={scenario.trailerType}
          onChange={(e) => handleChange('trailerType', e.target.value)}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Rate per Mile ($)</label>
          <input
            type="number"
            step="0.01"
            value={scenario.ratePerMile}
            onChange={(e) => handleChange('ratePerMile', parseFloat(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label>Total Rate ($)</label>
          <input
            type="number"
            value={scenario.totalRate}
            onChange={(e) => handleChange('totalRate', parseFloat(e.target.value))}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Accessorials</label>
        <input
          type="text"
          value={scenario.accessorials}
          onChange={(e) => handleChange('accessorials', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Securement Requirements</label>
        <input
          type="text"
          value={scenario.securementRequirements}
          onChange={(e) => handleChange('securementRequirements', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>TMS Update</label>
        <input
          type="text"
          value={scenario.tmsUpdate}
          onChange={(e) => handleChange('tmsUpdate', e.target.value)}
        />
      </div>
    </div>
  );
};
```

#### AgentConfigForm (`frontend/src/components/AgentConfigForm.tsx`)

```typescript
import React from 'react';
import type { AgentConfig } from '../types';

interface AgentConfigFormProps {
  agent: AgentConfig;
  label: string;
  onChange: (agent: AgentConfig) => void;
}

export const AgentConfigForm: React.FC<AgentConfigFormProps> = ({ agent, label, onChange }) => {
  const handleChange = (field: keyof AgentConfig, value: string) => {
    onChange({ ...agent, [field]: value });
  };

  return (
    <div className="agent-config-form">
      <h2>{label}</h2>
      
      <div className="form-group">
        <label>Agent Prompt</label>
        <textarea
          rows={6}
          value={agent.prompt}
          onChange={(e) => handleChange('prompt', e.target.value)}
          placeholder={`Enter the prompt for the ${agent.role} agent...`}
        />
      </div>

      <div className="form-group">
        <label>Acting Notes (Optional)</label>
        <textarea
          rows={3}
          value={agent.actingNotes || ''}
          onChange={(e) => handleChange('actingNotes', e.target.value)}
          placeholder="Optional notes to guide agent behavior..."
        />
      </div>
    </div>
  );
};
```

#### TranscriptDisplay (`frontend/src/components/TranscriptDisplay.tsx`)

```typescript
import React from 'react';
import type { ConversationTurn } from '../types';

interface TranscriptDisplayProps {
  transcript: ConversationTurn[];
}

export const TranscriptDisplay: React.FC<TranscriptDisplayProps> = ({ transcript }) => {
  return (
    <div className="transcript-display">
      <h2>Conversation Transcript</h2>
      <div className="transcript-content">
        {transcript.map((turn, index) => (
          <div key={index} className={`turn turn-${turn.speaker.toLowerCase()}`}>
            <div className="speaker">{turn.speaker}:</div>
            <div className="text">{turn.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### ConversationPlayer (`frontend/src/components/ConversationPlayer.tsx`)

```typescript
import React, { useRef } from 'react';

interface ConversationPlayerProps {
  audioUrl?: string;
}

export const ConversationPlayer: React.FC<ConversationPlayerProps> = ({ audioUrl }) => {
  const audioRef = useRef<HTMLAudioElement>(null);

  if (!audioUrl) {
    return (
      <div className="conversation-player">
        <p>Audio generation in progress...</p>
      </div>
    );
  }

  return (
    <div className="conversation-player">
      <h2>Audio Playback</h2>
      <audio ref={audioRef} controls src={audioUrl} className="audio-player">
        Your browser does not support the audio element.
      </audio>
    </div>
  );
};
```

### 5. Main App (`frontend/src/App.tsx`)

```typescript
import React, { useState } from 'react';
import { ScenarioForm } from './components/ScenarioForm';
import { AgentConfigForm } from './components/AgentConfigForm';
import { TranscriptDisplay } from './components/TranscriptDisplay';
import { ConversationPlayer } from './components/ConversationPlayer';
import { generateConversation } from './services/api';
import type { Scenario, AgentConfig, ConversationTurn } from './types';

const defaultScenario: Scenario = {
  loadId: 'HDX-2478',
  loadType: 'HVAC units',
  weight: 42000,
  pickupLocation: 'Dallas TX',
  pickupTime: '8 AM',
  pickupType: 'live',
  deliveryLocation: 'Atlanta GA',
  deliveryDeadline: 'before noon next day',
  trailerType: 'dry-van',
  ratePerMile: 2.10,
  totalRate: 1680,
  accessorials: 'none',
  securementRequirements: 'two-strap securement',
  tmsUpdate: 'Macro-1 update when empty',
};

const defaultDispatcherAgent: AgentConfig = {
  role: 'dispatcher',
  prompt: 'You are Tim, dispatcher at Dispatch Co trying to assign a driver for a load.',
  actingNotes: '',
};

const defaultDriverAgent: AgentConfig = {
  role: 'driver',
  prompt: 'You are Chris, a driver who is on his way to Dallas and agrees to the price.',
  actingNotes: '',
};

function App() {
  const [scenario, setScenario] = useState<Scenario>(defaultScenario);
  const [dispatcherAgent, setDispatcherAgent] = useState<AgentConfig>(defaultDispatcherAgent);
  const [driverAgent, setDriverAgent] = useState<AgentConfig>(defaultDriverAgent);
  const [transcript, setTranscript] = useState<ConversationTurn[]>([]);
  const [audioUrl, setAudioUrl] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await generateConversation({
        scenario,
        dispatcherAgent,
        driverAgent,
      });
      
      setTranscript(response.transcript);
      setAudioUrl(response.audioUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate conversation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Voice Agent Conversation Generator</h1>
      </header>

      <main>
        <div className="input-section">
          <ScenarioForm scenario={scenario} onChange={setScenario} />
          
          <AgentConfigForm
            agent={dispatcherAgent}
            label="Dispatcher Agent"
            onChange={setDispatcherAgent}
          />
          
          <AgentConfigForm
            agent={driverAgent}
            label="Driver Agent"
            onChange={setDriverAgent}
          />

          <div className="generate-section">
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="generate-button"
            >
              {loading ? 'Generating...' : 'Generate Conversation'}
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {transcript.length > 0 && (
          <div className="output-section">
            <TranscriptDisplay transcript={transcript} />
            <ConversationPlayer audioUrl={audioUrl} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
```

## Example Scenario

```json
{
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
    "prompt": "You are Tim, dispatcher at Dispatch Co trying to assign a driver for the following load: Full truckload of 42,000 lbs HVAC units picking up live at 8 AM in Dallas TX and delivering drop-off before noon next day in Atlanta GA, dry-van trailer, $2.10/mi ($1,680 all-in), no accessorials, two-strap securement, Macro-1 update when empty. With an ID of HDX-2478"
  },
  "driverAgent": {
    "role": "driver",
    "prompt": "You are Chris, a driver who is on his way to Dallas and agrees to the price."
  }
}
```

## Example Output Transcript

```
Dispatcher: Hey Chris, it's Tim over at Dispatch Co. You got a minute?
Driver: Hey Tim, yeah, go ahead.
Dispatcher: Cool — I've got a load I think might fit your schedule. It's picking up tomorrow morning out of Dallas, going to Atlanta. It's HVAC units — about 42,000 pounds, full truckload, dry van.
Driver: Okay, what's the pickup window?
Dispatcher: Pickup's at 8 AM sharp, appointment only. Delivery's the next day before noon, so you'll have about a day and a half to run it.
Driver: Alright, sounds doable. What's the rate looking like?
Dispatcher: We're at $2.10 a mile — total payout is $1,680. That's all-in, no extra stops, no lumper.
Driver: Alright, that's fair. Is it a live load or drop?
Dispatcher: Live load on pickup, drop at the receiver. They're usually pretty quick though, maybe an hour or so on each end.
Driver: Got it. Any special requirements?
Dispatcher: Just standard load securement — two straps minimum, no tarping needed. I'll send you the rate confirmation as soon as you say yes, and it'll show up in your TMS app right after that.
Driver: Okay, yeah, let's do it.
Dispatcher: Awesome. I'll book you on it now. You'll see the load in your app within a few minutes — load number is HDX-2478. Pickup address and contact are listed there. Just check in when you're empty tomorrow and send me a macro-1 update.
Driver: Will do. Thanks, Tim.
Dispatcher: Thanks, Chris. Talk soon — safe travels.
```

## Development Workflow

### Backend Setup

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
uvicorn src.api.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Next Steps

1. **Implement Livekit Voice Integration**
   - Set up Livekit server (cloud or self-hosted)
   - Integrate Livekit agents for voice synthesis
   - Implement audio generation pipeline

2. **Langfuse Integration** (Already Implemented)
   - All conversation generations are tracked
   - LLM performance is monitored automatically
   - Conversation quality can be analyzed in Langfuse dashboard

3. **Enhance Conversation Logic**
   - Improve conversation completion detection
   - Add conversation history management
   - Implement turn-by-turn generation with state

4. **UI/UX Improvements**
   - Add loading states
   - Improve styling
   - Add conversation history
   - Add export functionality

5. **Testing**
   - Unit tests for services
   - Integration tests for API
   - E2E tests for frontend

6. **Deployment**
   - Dockerize backend
   - Deploy frontend (Vercel/Netlify)
   - Set up environment variables
   - Configure CORS properly

## Notes

- The Livekit integration is simplified in this document. Full implementation requires proper setup of Livekit agents and voice synthesis services.
- OpenRouter API supports multiple models - choose based on cost/quality tradeoffs.
- **Langfuse is mandatory** - All LLM calls and conversations are automatically traced for observability. Make sure to set up your Langfuse account and configure the environment variables.
- Audio generation can be async - consider implementing background jobs for longer conversations.
- All conversation traces, LLM calls, and metadata are sent to Langfuse for analysis and monitoring.

