import React, { useEffect, useState } from 'react';
import { LiveKitRoom, RoomAudioRenderer, useParticipants, ParticipantTile } from '@livekit/components-react';
import type { RoomInfo } from '../types';
import './ConversationRoom.css';

interface ConversationRoomProps {
  roomInfo: RoomInfo;
}

function RoomParticipants() {
  const participants = useParticipants();
  
  return (
    <div className="participants-grid">
      {participants.map((participant) => (
        <div key={participant.identity} className="participant-card">
          <div className="participant-icon">
            {participant.identity === 'dispatcher' ? '👔' : '🚚'}
          </div>
          <h3>{participant.name || participant.identity}</h3>
          <div className="audio-indicator">
            {participant.isSpeaking ? '🔊 Speaking...' : '🔇 Listening'}
          </div>
        </div>
      ))}
    </div>
  );
}

export const ConversationRoom: React.FC<ConversationRoomProps> = ({ roomInfo }) => {
  const [roomState, setRoomState] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

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
        options={{
          publishDefaults: {
            audio: false,
            video: false,
          },
        }}
        onConnected={() => setRoomState('connected')}
        onDisconnected={() => setRoomState('disconnected')}
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

          {roomState === 'connected' && (
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

          {roomState === 'disconnected' && (
            <div className="room-status">
              <p>❌ Disconnected from room</p>
            </div>
          )}
        </div>
      </LiveKitRoom>
    </div>
  );
};

