import axios from 'axios';
import type { ConversationRequest, RoomInfo, ConversationStatus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const createRoom = async (
  request: ConversationRequest
): Promise<RoomInfo> => {
  const response = await api.post<RoomInfo>(
    '/api/v1/rooms/create',
    request
  );
  return response.data;
};

export const getRoomStatus = async (roomName: string) => {
  const response = await api.get(`/api/v1/rooms/${roomName}/status`);
  return response.data;
};

export const getRecording = async (roomName: string) => {
  const response = await api.get(`/api/v1/rooms/${roomName}/recording`);
  return response.data;
};

export const getTranscript = async (roomName: string) => {
  const response = await api.get(`/api/v1/rooms/${roomName}/transcript`);
  return response.data;
};

export const checkConversationStatus = async (roomName: string) => {
  try {
    const status = await getRoomStatus(roomName);
    return {
      status: status.participantCount === 0 ? 'concluded' : 'active',
      conversationId: roomName,
      participants: status.participants || []
    };
  } catch (error) {
    return {
      status: 'error',
      conversationId: roomName,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};

export const uploadAudio = async (roomName: string, audioBlob: Blob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, `${roomName}.mp3`);
  
  const response = await api.post(
    `/api/v1/rooms/${roomName}/upload-audio`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for large files
    }
  );
  return response.data;
};

export const getAudioUrl = (roomName: string): string => {
  return `${API_BASE_URL}/api/v1/rooms/${roomName}/audio`;
};

