import React, { useState, useEffect } from 'react';
import type { ConversationTurn } from '../types';
import './ConversationPlayer.css';

interface ConversationPlayerProps {
  conversationId: string;
  recordingUrl?: string;
  transcript?: ConversationTurn[];
}

export const ConversationPlayer: React.FC<ConversationPlayerProps> = ({
  conversationId,
  recordingUrl,
  transcript = []
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTurnIndex, setCurrentTurnIndex] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNext = () => {
    if (currentTurnIndex < transcript.length - 1) {
      setCurrentTurnIndex(currentTurnIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentTurnIndex > 0) {
      setCurrentTurnIndex(currentTurnIndex - 1);
    }
  };

  const handleReset = () => {
    setCurrentTurnIndex(0);
    setIsPlaying(false);
  };

  const currentTurn = transcript[currentTurnIndex];
  const progress = transcript.length > 0 ? ((currentTurnIndex + 1) / transcript.length) * 100 : 0;

  return (
    <div className="conversation-player">
      <div className="player-header">
        <h3>🎙️ Conversation Playback</h3>
        <div className="conversation-id">ID: {conversationId}</div>
      </div>

      {recordingUrl && (
        <div className="audio-player">
          <audio
            src={recordingUrl}
            controls
            className="audio-control"
          />
          <p className="audio-hint">🎧 Full conversation recording</p>
        </div>
      )}

      {transcript.length > 0 && (
        <>
          <div className="transcript-viewer">
            <div className="current-turn">
              {currentTurn && (
                <>
                  <div className={`speaker ${currentTurn.speaker.toLowerCase()}`}>
                    {currentTurn.speaker === 'Dispatcher' ? '👔' : '🚚'} {currentTurn.speaker}
                  </div>
                  <div className="turn-text">{currentTurn.text}</div>
                  <div className="turn-timestamp">
                    {new Date(currentTurn.timestamp).toLocaleTimeString()}
                  </div>
                </>
              )}
            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="progress-text">
              Turn {currentTurnIndex + 1} of {transcript.length}
            </div>
          </div>

          <div className="player-controls">
            <button
              onClick={handlePrevious}
              disabled={currentTurnIndex === 0}
              className="control-btn"
              title="Previous turn"
            >
              ⏮ Previous
            </button>

            <button
              onClick={handlePlayPause}
              className="control-btn play-btn"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? '⏸ Pause' : '▶️ Play'}
            </button>

            <button
              onClick={handleNext}
              disabled={currentTurnIndex === transcript.length - 1}
              className="control-btn"
              title="Next turn"
            >
              Next ⏭
            </button>

            <button
              onClick={handleReset}
              className="control-btn"
              title="Reset to beginning"
            >
              🔄 Reset
            </button>
          </div>

          <div className="speed-control">
            <label>Playback Speed: </label>
            <select
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              className="speed-select"
            >
              <option value={0.75}>0.75x</option>
              <option value={1}>1x (Normal)</option>
              <option value={1.25}>1.25x</option>
              <option value={1.5}>1.5x</option>
              <option value={2}>2x</option>
            </select>
          </div>

          <div className="transcript-list">
            <h4>📋 Full Transcript</h4>
            <div className="transcript-scroll">
              {transcript.map((turn, idx) => (
                <div
                  key={idx}
                  className={`transcript-turn ${
                    idx === currentTurnIndex ? 'active' : ''
                  }`}
                  onClick={() => {
                    setCurrentTurnIndex(idx);
                    setIsPlaying(false);
                  }}
                >
                  <div className="turn-number">{idx + 1}</div>
                  <div className="turn-speaker">
                    {turn.speaker === 'Dispatcher' ? '👔' : '🚚'}
                  </div>
                  <div className="turn-content">
                    <strong>{turn.speaker}:</strong>
                    <p>{turn.text.substring(0, 60)}...</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {transcript.length === 0 && !recordingUrl && (
        <div className="no-content">
          <p>No conversation recording available yet</p>
          <p className="hint">The conversation will appear here once it completes</p>
        </div>
      )}
    </div>
  );
};
