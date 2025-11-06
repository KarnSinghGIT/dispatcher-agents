import React, { useState, useEffect, useRef } from 'react';
import { LiveKitRoom, RoomAudioRenderer, useParticipants, useRoomContext } from '@livekit/components-react';
import type { RoomInfo } from '../types';
import { ConversationPlayer } from './ConversationPlayer';
import { uploadAudio, getAudioUrl } from '../services/api';
import './ConversationRoom.css';

interface ConversationRoomProps {
  roomInfo: RoomInfo;
}

function RoomParticipants() {
  const participants = useParticipants();
  const [showWarning, setShowWarning] = useState(false);
  
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

// Audio recorder component that uses the LiveKit room context
function AudioRecorder({ 
  roomName, 
  onRecordingComplete 
}: { 
  roomName: string; 
  onRecordingComplete: (audioUrl: string) => void;
}) {
  const room = useRoomContext();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioSourcesRef = useRef<MediaStreamAudioSourceNode[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    if (!room) return;

    let recorder: MediaRecorder | null = null;
    let destination: MediaStreamAudioDestinationNode | null = null;

    const startRecording = async () => {
      try {
        console.log('[RECORDER] Starting audio recording...');
        
        // Create audio context and destination
        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;
        destination = audioContext.createMediaStreamDestination();
        
        // Function to connect a track to recording
        const connectTrack = (track: MediaStreamTrack, participantIdentity: string) => {
          try {
            const mediaStream = new MediaStream([track]);
            const source = audioContext.createMediaStreamSource(mediaStream);
            source.connect(destination!);
            audioSourcesRef.current.push(source);
            console.log(`[RECORDER] ✓ Connected audio from: ${participantIdentity}`);
          } catch (error) {
            console.error(`[RECORDER] Failed to connect track from ${participantIdentity}:`, error);
          }
        };

        // Connect existing tracks
        let trackCount = 0;
        room.remoteParticipants.forEach((participant) => {
          participant.audioTrackPublications.forEach((_publication) => {
            if (_publication.track && _publication.track.mediaStreamTrack) {
              connectTrack(_publication.track.mediaStreamTrack, participant.identity);
              trackCount++;
            }
          });
        });

        console.log(`[RECORDER] Connected ${trackCount} existing audio tracks`);

        // Listen for new tracks being subscribed
        const handleTrackSubscribed = (
          track: any,
          publication: any,
          participant: any
        ) => {
          if (track.kind === 'audio' && track.mediaStreamTrack) {
            console.log(`[RECORDER] New audio track from: ${participant.identity}`);
            connectTrack(track.mediaStreamTrack, participant.identity);
          }
        };

        room.on('trackSubscribed', handleTrackSubscribed);

        // Create MediaRecorder with better options
        let mimeType = 'audio/webm;codecs=opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = 'audio/webm';
        }
        
        const options = { 
          mimeType,
          audioBitsPerSecond: 128000 // 128 kbps
        };
        
        recorder = new MediaRecorder(destination.stream, options);
        mediaRecorderRef.current = recorder;
        
        recorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
            console.log(`[RECORDER] Chunk received: ${(event.data.size / 1024).toFixed(2)}KB`);
          }
        };
        
        recorder.onstop = async () => {
          console.log('[RECORDER] Recording stopped, processing...');
          setIsRecording(false);
          setIsUploading(true);
          
          // Cleanup audio context
          await new Promise(resolve => setTimeout(resolve, 500)); // Wait for final chunks
          
          try {
            room.off('trackSubscribed', handleTrackSubscribed);
          } catch (e) {
            console.log('[RECORDER] Could not unsubscribe from room events:', e);
          }
          
          audioSourcesRef.current.forEach(source => {
            try {
              source.disconnect();
            } catch (e) {}
          });
          audioSourcesRef.current = [];
          
          if (audioContextRef.current) {
            try {
              audioContextRef.current.close();
            } catch (e) {}
            audioContextRef.current = null;
          }

          console.log(`[RECORDER] Total chunks: ${audioChunksRef.current.length}`);
          
          if (audioChunksRef.current.length === 0) {
            console.log('[RECORDER] [ERROR] No audio data recorded');
            setIsUploading(false);
            return;
          }

          // Create blob from chunks
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const sizeMB = audioBlob.size / (1024 * 1024);
          console.log(`[RECORDER] Total audio size: ${sizeMB.toFixed(2)}MB (${audioChunksRef.current.length} chunks)`);
          
          if (sizeMB < 0.001) {
            console.log('[RECORDER] [ERROR] Recording too small (< 1KB), skipping upload');
            setIsUploading(false);
            return;
          }
          
          try {
            // Upload to backend
            console.log(`[RECORDER] Uploading ${sizeMB.toFixed(2)}MB to backend...`);
            const result = await uploadAudio(roomName, audioBlob);
            console.log('[RECORDER] [OK] Upload successful:', result.filename);
            
            // Wait a moment for file to be written
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Get the audio URL
            const audioUrl = getAudioUrl(roomName);
            console.log('[RECORDER] [OK] Calling onRecordingComplete with URL:', audioUrl);
            onRecordingComplete(audioUrl);
          } catch (error) {
            console.error('[RECORDER] [ERROR] Upload failed:', error);
            setIsUploading(false);
          }
        };

        // Start recording
        recorder.start(1000); // Collect data every second
        setIsRecording(true);
        console.log('[RECORDER] ✓ Recording started successfully');
        
      } catch (error) {
        console.error('[RECORDER] ✗ Failed to start recording:', error);
      }
    };

    // Wait for participants and their tracks to be ready
    const timer = setTimeout(() => {
      const participantCount = room.remoteParticipants.size;
      console.log(`[RECORDER] Room has ${participantCount} participants`);
      
      if (participantCount > 0) {
        startRecording();
      } else {
        console.log('[RECORDER] ⚠️  No participants yet, recording may not capture audio');
        // Start anyway, tracks will be connected when they arrive
        startRecording();
      }
    }, 3000); // Wait 3 seconds for participants to fully join

    return () => {
      clearTimeout(timer);
      if (recorder && recorder.state !== 'inactive') {
        console.log('[RECORDER] Stopping recording (cleanup)');
        recorder.stop();
      }
    };
  }, [room, roomName, onRecordingComplete]);

  // Stop recording when component unmounts or room disconnects
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        console.log('[RECORDER] Stopping recording (cleanup)');
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  // Also stop recording when room disconnects
  useEffect(() => {
    return () => {
      // This will be called on unmount
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        console.log('[RECORDER] Force stopping on room disconnect');
        mediaRecorderRef.current.stop();
      }
    };
  }, [roomName]);

  return (
    <div className="recording-status">
      {isRecording && (
        <div className="recording-indicator">
          <div className="recording-dot"></div>
          <span>Recording conversation...</span>
        </div>
      )}
      {isUploading && (
        <div className="uploading-indicator">
          <div className="spinner-small"></div>
          <span>Processing audio...</span>
        </div>
      )}
    </div>
  );
}

export const ConversationRoom: React.FC<ConversationRoomProps> = ({ roomInfo }) => {
  const [roomState, setRoomState] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [showPlayer, setShowPlayer] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | undefined>(undefined);

  const handleRecordingComplete = (url: string) => {
    console.log('[ROOM] Recording complete, showing player with:', url);
    setAudioUrl(url);
    setShowPlayer(true);
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
        onConnected={() => {
          console.log('[ROOM] Connected to LiveKit room');
          setRoomState('connected');
        }}
        onDisconnected={() => {
          console.log('[ROOM] Disconnected from room, waiting for upload...');
          setRoomState('disconnected');
        }}
        className="livekit-room-container"
      >
        {/* Render audio for all participants */}
        <RoomAudioRenderer />
        
        {/* Audio recorder */}
        {roomState === 'connected' && (
          <AudioRecorder 
            roomName={roomInfo.roomName} 
            onRecordingComplete={handleRecordingComplete}
          />
        )}
        
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
              
              {showPlayer && audioUrl && (
                <div className="inline-player-section">
                  <ConversationPlayer
                    conversationId={roomInfo.conversationId}
                    audioUrl={audioUrl}
                  />
                </div>
              )}
              
              {!showPlayer && (
                <div className="instructions">
                  <p>💡 You are observing the live voice conversation</p>
                  <p>The dispatcher and driver agents are talking in real-time</p>
                  <p className="hint">The audio recording will be available below after the conversation ends</p>
                </div>
              )}
            </>
          )}

          {roomState === 'disconnected' && !showPlayer && (
            <div className="room-status">
              <p>❌ Disconnected from room</p>
              <button
                onClick={() => setShowPlayer(true)}
                className="show-player-btn"
              >
                🎙️ Play Recording
              </button>
            </div>
          )}
        </div>
      </LiveKitRoom>
    </div>
  );
};
