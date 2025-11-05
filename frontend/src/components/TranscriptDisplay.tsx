import React from 'react';
import type { ConversationTurn } from '../types';
import './TranscriptDisplay.css';

interface TranscriptDisplayProps {
  transcript: ConversationTurn[];
}

export const TranscriptDisplay: React.FC<TranscriptDisplayProps> = ({ transcript }) => {
  if (transcript.length === 0) {
    return null;
  }

  return (
    <div className="transcript-display">
      <h2>Conversation Transcript</h2>
      <div className="transcript-content">
        {transcript.map((turn, index) => (
          <div key={index} className={`turn turn-${turn.speaker.toLowerCase()}`}>
            <div className="speaker-badge">{turn.speaker}</div>
            <div className="text">{turn.text}</div>
            <div className="timestamp">
              {new Date(turn.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

