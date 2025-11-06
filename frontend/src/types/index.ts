export interface Scenario {
  loadId: string;
  loadType: string;
  weight: number;
  pickupLocation: string;
  pickupTime: string;
  pickupType: string;
  deliveryLocation: string;
  deliveryDeadline: string;
  trailerType: string;
  ratePerMile: number;
  totalRate: number;
  accessorials: string;
  securementRequirements: string;
  tmsUpdate: string;
}

export interface AgentConfig {
  role: 'dispatcher' | 'driver';
  prompt: string;
  actingNotes?: string;
}

export interface ConversationStatus {
  status: 'active' | 'concluded' | 'recording' | 'ready_for_playback';
  conversationId: string;
  recordingUrl?: string;
  transcript?: ConversationTurn[];
}

export interface ConversationRequest {
  scenario: Scenario;
  dispatcherAgent: AgentConfig;
  driverAgent: AgentConfig;
}

export interface ConversationTurn {
  speaker: string;
  text: string;
  timestamp: string;
}

export interface ConversationResponse {
  conversationId: string;
  transcript: ConversationTurn[];
  audioUrl?: string;
}

export interface RoomInfo {
  roomName: string;
  roomToken: string;
  livekitUrl: string;
  conversationId: string;
}

