import React, { useRef } from 'react';
import './ConversationPlayer.css';

interface ConversationPlayerProps {
  audioUrl?: string;
}

export const ConversationPlayer: React.FC<ConversationPlayerProps> = ({ audioUrl }) => {
  const audioRef = useRef<HTMLAudioElement>(null);

  if (!audioUrl) {
    return (
      <div className="conversation-player">
        <div className="placeholder">
          <p>🎵 Audio generation will be implemented in later milestones</p>
          <p className="note">For now, enjoy reading the transcript above!</p>
        </div>
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

