import React, { useState } from 'react';
import { ScenarioForm } from './components/ScenarioForm';
import { AgentConfigForm } from './components/AgentConfigForm';
import { ConversationRoom } from './components/ConversationRoom';
import { createRoom } from './services/api';
import type { Scenario, AgentConfig, RoomInfo } from './types';
import './App.css';

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
  prompt: `You are Tim, a friendly and professional dispatcher at Dispatch Co. 

You are calling a driver named Chris about a load opportunity.

Your goal is to:
1. Greet Chris warmly
2. Present the load details clearly
3. Answer any questions he has
4. Get his commitment to take the load
5. Provide next steps

Be conversational, professional, and efficient. Keep responses natural and brief.

Wait for responses before continuing.`,
  actingNotes: '',
};

const defaultDriverAgent: AgentConfig = {
  role: 'driver',
  prompt: `You are Chris, an experienced truck driver who is currently on the road.

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

Wait for Tim to greet you first, then respond naturally to his questions and information.`,
  actingNotes: '',
};

function App() {
  const [scenario, setScenario] = useState<Scenario>(defaultScenario);
  const [dispatcherAgent, setDispatcherAgent] = useState<AgentConfig>(defaultDispatcherAgent);
  const [driverAgent, setDriverAgent] = useState<AgentConfig>(defaultDriverAgent);
  const [roomInfo, setRoomInfo] = useState<RoomInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartConversation = async () => {
    setLoading(true);
    setError(null);
    setRoomInfo(null);
    
    try {
      const response = await createRoom({
        scenario,
        dispatcherAgent,
        driverAgent,
      });
      
      setRoomInfo(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create room';
      setError(errorMessage);
      console.error('Error creating room:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🎙️ AI Voice Agent Conversation</h1>
        <p>Watch two AI agents have a real-time voice conversation via WebRTC</p>
      </header>

      <main className="main">
        {!roomInfo ? (
          <div className="input-section">
            <ScenarioForm scenario={scenario} onChange={setScenario} />
            
            <AgentConfigForm
              agent={dispatcherAgent}
              label="Dispatcher Agent Configuration"
              onChange={setDispatcherAgent}
            />
            
            <AgentConfigForm
              agent={driverAgent}
              label="Driver Agent Configuration"
              onChange={setDriverAgent}
            />

            <div className="generate-section">
              <button
                onClick={handleStartConversation}
                disabled={loading}
                className="generate-button"
              >
                {loading ? 'Creating Room...' : '🚀 Start Live Conversation'}
              </button>
              {loading && (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>Creating LiveKit room...</p>
                  <p className="hint">Agents will join automatically</p>
                </div>
              )}
            </div>

            {error && (
              <div className="error-message">
                <h3>❌ Error</h3>
                <p>{error}</p>
                <p className="error-hint">
                  <strong>Checklist:</strong>
                  <br />• Backend server is running (http://localhost:8000)
                  <br />• LiveKit server is running (ws://localhost:7880)
                  <br />• LiveKit credentials are in backend/.env
                  <br />• Multi-agent worker is running (see instructions below)
                  <br />• Check terminal logs for "Worker registered" and both agents starting
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="conversation-section">
            <ConversationRoom roomInfo={roomInfo} />
            
            <div className="controls">
              <button
                onClick={() => setRoomInfo(null)}
                className="reset-button"
              >
                ← Start New Conversation
              </button>
            </div>

            <div className="agent-status">
              <h3>📡 Important Setup Instructions</h3>
              <div className="setup-steps">
                <div className="setup-step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h4>Start LiveKit Server</h4>
                    <p>Make sure LiveKit server is running on localhost:7880</p>
                  </div>
                </div>
                <div className="setup-step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h4>Start Multi-Agent Worker</h4>
                    <pre>
cd backend && python agents/multi_agent_worker.py dev
                    </pre>
                    <p className="hint">This single worker runs both agents in the same room</p>
                  </div>
                </div>
                <div className="setup-step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h4>Wait for Confirmation</h4>
                    <p>You should see "Worker registered" and then both agent sessions starting</p>
                  </div>
                </div>
              </div>
              <p className="warning-note">⚠️ Agents must be running BEFORE creating a room!</p>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
      </footer>
    </div>
  );
}

export default App;

