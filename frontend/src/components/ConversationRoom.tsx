import React, { useState, useEffect } from 'react';
import { LiveKitRoom, RoomAudioRenderer, useParticipants } from '@livekit/components-react';
import type { RoomInfo } from '../types';
import { ConversationPlayer } from './ConversationPlayer';
import { checkConversationStatus, getRecording } from '../services/api';
import './ConversationRoom.css';

interface ConversationRoomProps {
  roomInfo: RoomInfo;
}

function RoomParticipants() {
  const participants = useParticipants();
  const [showWarning, setShowWarning] = useState(false);
  const [conversationConcluded, setConversationConcluded] = useState(false);
  const [recordingUrl, setRecordingUrl] = useState<string | undefined>();
  const [transcriptData, setTranscriptData] = useState<any[]>([]);
  
  // Filter out the observer (frontend user)
  const agents = participants.filter(p => 
    !p.identity?.toLowerCase().includes('observer')
  );
  
  const hasDispatcher = agents.some(p => 
    p.name?.toLowerCase().includes('dispatcher') || 
    p.name?.toLowerCase().includes('tim') ||
    p.identity?.toLowerCase().includes('dispatcher')
  );
  
  const hasDriver = agents.some(p =>
    p.name?.toLowerCase().includes('driver') || 
    p.name?.toLowerCase().includes('chris') ||
    p.identity?.toLowerCase().includes('driver')
  );
  
  // Show warning if no agents join within 10 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      if (agents.length === 0) {
        setShowWarning(true);
      }
    }, 10000);
    
    return () => clearTimeout(timer);
  }, [agents.length]);

  // Monitor for conversation conclusion (agents left room)
  useEffect(() => {
    if (agents.length === 0 && !conversationConcluded && showWarning === false) {
      // Conversation has concluded
      setConversationConcluded(true);
      console.log('Conversation concluded - agents left room');
      
      // Try to get recording info
      // Note: This will need to be fetched with the room name
    }
  }, [agents.length, conversationConcluded, showWarning]);
  
  return (
    <div>
      {agents.length === 0 && !showWarning && (
        <div className="waiting-agents">
          <div className="spinner"></div>
          <p>⏳ Waiting for agents to join...</p>
          <p className="hint">This should take 2-5 seconds</p>
        </div>
      )}
      
      {agents.length === 0 && showWarning && (
        <div className="agents-warning">
          <h3>⚠️ No Agents Joined</h3>
          <p>The multi-agent worker doesn't seem to be running.</p>
          <p><strong>Please start the multi-agent worker:</strong></p>
          <pre>
cd backend && python agents/multi_agent_worker.py dev
          </pre>
          <p className="hint">This single worker runs both agents. After starting it, create a new room.</p>
        </div>
      )}
      
      {agents.length > 0 && (
        <>
          <div className="agent-status-summary">
            <div className={`agent-indicator ${hasDispatcher ? 'active' : 'inactive'}`}>
              👔 Dispatcher {hasDispatcher ? '✓' : '✗'}
            </div>
            <div className={`agent-indicator ${hasDriver ? 'active' : 'inactive'}`}>
              🚚 Driver {hasDriver ? '✓' : '✗'}
            </div>
          </div>
          
          <div className="participants-grid">
            {agents.map((participant) => {
              const isDispatcher = participant.name?.toLowerCase().includes('dispatcher') || 
                                  participant.name?.toLowerCase().includes('tim') ||
                                  participant.identity?.toLowerCase().includes('dispatcher');
              const isDriver = participant.name?.toLowerCase().includes('driver') || 
                              participant.name?.toLowerCase().includes('chris') ||
                              participant.identity?.toLowerCase().includes('driver');
              
              return (
                <div key={participant.identity} className="participant-card">
                  <div className="participant-icon">
                    {isDispatcher ? '👔' : isDriver ? '🚚' : '👤'}
                  </div>
                  <h3>{participant.name || participant.identity}</h3>
                  <div className="audio-indicator">
                    {participant.isSpeaking ? '🔊 Speaking...' : '🔇 Listening'}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export const ConversationRoom: React.FC<ConversationRoomProps> = ({ roomInfo }) => {
  const [roomState, setRoomState] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [showPlayer, setShowPlayer] = useState(false);
  const [playerData, setPlayerData] = useState<{ recordingUrl?: string; transcript?: any[] }>({});

  // Helper function to extract participant info from room
  const fetchRecordingData = async () => {
    try {
      const recordingData = await getRecording(roomInfo.roomName);
      setPlayerData({
        recordingUrl: recordingData.recordings?.[0]?.location,
        transcript: [] // Will be populated if we have transcript data
      });
    } catch (error) {
      console.error('Could not fetch recording:', error);
    }
  };

  return (
    <div className="conversation-room">
      <div className="room-header">
        <h2>🎙️ Live Voice Conversation</h2>
        <div className="room-info">
          <span className="room-name">Room: {roomInfo.roomName}</span>
          <span className={`status-badge status-${roomState}`}>
            {roomState}
          </span>
        </div>
      </div>

      <LiveKitRoom
        token={roomInfo.roomToken}
        serverUrl={roomInfo.livekitUrl}
        connect={true}
        audio={false}
        video={false}
        onConnected={() => setRoomState('connected')}
        onDisconnected={() => {
          setRoomState('disconnected');
          setShowPlayer(true);
          fetchRecordingData();
        }}
        className="livekit-room-container"
      >
        {/* Render audio for all participants */}
        <RoomAudioRenderer />
        
        <div className="room-content">
          {roomState === 'connecting' && (
            <div className="room-status">
              <div className="spinner"></div>
              <p>Connecting to room...</p>
              <p className="hint">Agents will join shortly</p>
            </div>
          )}

          {roomState === 'connected' && !showPlayer && (
            <>
              <div className="listening-indicator">
                <div className="pulse-dot"></div>
                <span>Listening to conversation...</span>
              </div>
              
              <RoomParticipants />
              
              <div className="instructions">
                <p>💡 You are observing the live voice conversation</p>
                <p>The dispatcher and driver agents are talking in real-time</p>
              </div>
            </>
          )}

          {showPlayer && (
            <div className="playback-section">
              <ConversationPlayer
                conversationId={roomInfo.conversationId}
                recordingUrl={playerData.recordingUrl}
                transcript={playerData.transcript}
              />
            </div>
          )}

          {roomState === 'disconnected' && !showPlayer && (
            <div className="room-status">
              <p>❌ Disconnected from room</p>
              <button
                onClick={() => setShowPlayer(true)}
                className="show-player-btn"
              >
                🎙️ Replay Conversation
              </button>
            </div>
          )}
        </div>
      </LiveKitRoom>
    </div>
  );
};

