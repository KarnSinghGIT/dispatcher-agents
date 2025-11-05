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
  prompt: 'You are Tim, dispatcher at Dispatch Co. Be friendly and professional when presenting loads.',
  actingNotes: '',
};

const defaultDriverAgent: AgentConfig = {
  role: 'driver',
  prompt: 'You are Chris, an experienced driver. Ask relevant questions before committing to loads.',
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
                  Make sure:
                  <br />• Backend server is running
                  <br />• LiveKit credentials are configured
                  <br />• Agent workers are started
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
              <h3>📡 Agent Instructions</h3>
              <p>Make sure both agent workers are running:</p>
              <pre>
                Terminal 1: python backend/agents/dispatcher_agent.py{'\n'}
                Terminal 2: python backend/agents/driver_agent.py
              </pre>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Powered by LiveKit + OpenAI Realtime API</p>
      </footer>
    </div>
  );
}

export default App;

