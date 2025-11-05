import axios from 'axios';
import type { ConversationRequest, RoomInfo } from '../types';

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

