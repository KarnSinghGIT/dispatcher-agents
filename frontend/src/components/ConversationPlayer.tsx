import React, { useState, useEffect, useRef } from 'react';
import './ConversationPlayer.css';

interface ConversationPlayerProps {
  conversationId: string;
  audioUrl?: string;
}

export const ConversationPlayer: React.FC<ConversationPlayerProps> = ({
  conversationId,
  audioUrl
}) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isBuffering, setIsBuffering] = useState(!audioUrl);
  const [retryCount, setRetryCount] = useState(0);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Poll for audio file if buffering
  useEffect(() => {
    if (!audioUrl || !isBuffering) return;

    console.log(`[PLAYER] Polling for audio file... (attempt ${retryCount + 1})`);
    
    const poll = async () => {
      try {
        const response = await fetch(audioUrl, { method: 'HEAD' });
        if (response.ok) {
          console.log('[PLAYER] ✓ Audio file ready!');
          setIsBuffering(false);
          // Force reload the audio element
          if (audioRef.current) {
            audioRef.current.load();
          }
        }
      } catch (error) {
        console.log('[PLAYER] Audio not ready yet, retrying...');
        setRetryCount(prev => prev + 1);
      }
    };

    // Poll every 2 seconds
    pollingRef.current = setInterval(poll, 2000);

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [audioUrl, isBuffering, retryCount]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => {
      setDuration(audio.duration);
      setIsBuffering(false); // File loaded successfully
    };
    const handleEnded = () => setIsPlaying(false);
    const handleError = () => {
      console.log('[PLAYER] Audio error, will retry...');
      setIsBuffering(true);
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, []);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newTime = parseFloat(e.target.value);
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const newVolume = parseFloat(e.target.value);
    audio.volume = newVolume;
    setVolume(newVolume);
  };

  const skip = (seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    audio.currentTime = Math.max(0, Math.min(audio.duration, audio.currentTime + seconds));
  };

  const formatTime = (seconds: number): string => {
    if (isNaN(seconds) || !isFinite(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="conversation-player">
      <div className="player-header">
        <h3>🎙️ Conversation Recording</h3>
        <div className="conversation-id">ID: {conversationId}</div>
      </div>

      {audioUrl ? (
        <div className="audio-player-container">
          {isBuffering && (
            <div className="buffering-status">
              <div className="buffering-spinner"></div>
              <p>Waiting for audio to be ready...</p>
              <p className="buffering-hint">Recording is still in progress. Audio will start playing once it's available.</p>
            </div>
          )}
          
          <audio
            ref={audioRef}
            src={audioUrl}
            preload="metadata"
          />

          {!isBuffering && (
          <div className="audio-player-custom">
            <div className="player-main">
              <button
                onClick={togglePlayPause}
                className="play-button"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? '⏸' : '▶️'}
              </button>

              <div className="time-display">{formatTime(currentTime)}</div>

              <div className="seek-bar-container">
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleSeek}
                  className="seek-bar"
                />
                <div
                  className="seek-progress"
                  style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                />
              </div>

              <div className="time-display">{formatTime(duration)}</div>
            </div>

            <div className="player-controls">
              <button
                onClick={() => skip(-10)}
                className="control-btn"
                title="Rewind 10 seconds"
              >
                ⏪ -10s
              </button>

              <button
                onClick={() => skip(10)}
                className="control-btn"
                title="Forward 10 seconds"
              >
                +10s ⏩
              </button>

              <div className="volume-control">
                <span className="volume-icon">
                  {volume === 0 ? '🔇' : volume < 0.5 ? '🔉' : '🔊'}
                </span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="volume-slider"
                />
              </div>
            </div>

            <div className="player-info">
              <p className="audio-hint">🎧 Full conversation audio recording in high quality</p>
            </div>
          </div>
          )}
        </div>
      ) : (
        <div className="no-audio">
          <div className="loading-spinner"></div>
          <p>⏳ Processing audio recording...</p>
          <p className="hint">The audio will be available shortly after the conversation completes</p>
        </div>
      )}
    </div>
  );
};
