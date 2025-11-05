"""Pydantic schemas for API requests and responses."""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Scenario(BaseModel):
    """Load scenario details."""
    loadId: str = Field(..., description="Load identifier", example="HDX-2478")
    loadType: str = Field(..., description="Type of load", example="HVAC units")
    weight: int = Field(..., description="Weight in pounds", example=42000)
    pickupLocation: str = Field(..., description="Pickup location", example="Dallas TX")
    pickupTime: str = Field(..., description="Pickup time", example="8 AM")
    pickupType: str = Field(..., description="Pickup type (live/drop)", example="live")
    deliveryLocation: str = Field(..., description="Delivery location", example="Atlanta GA")
    deliveryDeadline: str = Field(..., description="Delivery deadline", example="before noon next day")
    trailerType: str = Field(..., description="Trailer type", example="dry-van")
    ratePerMile: float = Field(..., description="Rate per mile in dollars", example=2.10)
    totalRate: float = Field(..., description="Total rate in dollars", example=1680.0)
    accessorials: str = Field(..., description="Accessorial services", example="none")
    securementRequirements: str = Field(..., description="Load securement requirements", example="two-strap securement")
    tmsUpdate: str = Field(..., description="TMS update requirements", example="Macro-1 update when empty")

    class Config:
        json_schema_extra = {
            "example": {
                "loadId": "HDX-2478",
                "loadType": "HVAC units",
                "weight": 42000,
                "pickupLocation": "Dallas TX",
                "pickupTime": "8 AM",
                "pickupType": "live",
                "deliveryLocation": "Atlanta GA",
                "deliveryDeadline": "before noon next day",
                "trailerType": "dry-van",
                "ratePerMile": 2.10,
                "totalRate": 1680.0,
                "accessorials": "none",
                "securementRequirements": "two-strap securement",
                "tmsUpdate": "Macro-1 update when empty"
            }
        }


class AgentConfig(BaseModel):
    """Agent configuration."""
    role: str = Field(..., description="Agent role (dispatcher/driver)", example="dispatcher")
    prompt: str = Field(..., description="Agent system prompt", example="You are Tim, dispatcher at Dispatch Co.")
    actingNotes: Optional[str] = Field(None, description="Optional acting notes for the agent")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "dispatcher",
                "prompt": "You are Tim, dispatcher at Dispatch Co trying to assign a driver for a load.",
                "actingNotes": "Speak professionally but friendly."
            }
        }


class ConversationRequest(BaseModel):
    """Request to generate a conversation."""
    scenario: Scenario
    dispatcherAgent: AgentConfig
    driverAgent: AgentConfig

    class Config:
        json_schema_extra = {
            "example": {
                "scenario": Scenario.Config.json_schema_extra["example"],
                "dispatcherAgent": {
                    "role": "dispatcher",
                    "prompt": "You are Tim, dispatcher at Dispatch Co."
                },
                "driverAgent": {
                    "role": "driver",
                    "prompt": "You are Chris, a driver."
                }
            }
        }


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""
    speaker: str = Field(..., description="Speaker name (Dispatcher/Driver)", example="Dispatcher")
    text: str = Field(..., description="What the speaker said", example="Hey Chris, it's Tim over at Dispatch Co.")
    timestamp: str = Field(..., description="ISO timestamp of the turn", example="2024-01-01T12:00:00")

    class Config:
        json_schema_extra = {
            "example": {
                "speaker": "Dispatcher",
                "text": "Hey Chris, it's Tim over at Dispatch Co. You got a minute?",
                "timestamp": "2024-01-01T12:00:00.000000"
            }
        }


class ConversationResponse(BaseModel):
    """Response containing generated conversation."""
    conversationId: str = Field(..., description="Unique conversation identifier")
    transcript: List[ConversationTurn] = Field(..., description="List of conversation turns")
    audioUrl: Optional[str] = Field(None, description="URL to audio file (if generated)")

    class Config:
        json_schema_extra = {
            "example": {
                "conversationId": "2024-01-01T12:00:00.000000",
                "transcript": [
                    {
                        "speaker": "Dispatcher",
                        "text": "Hey Chris, it's Tim over at Dispatch Co. You got a minute?",
                        "timestamp": "2024-01-01T12:00:00.000000"
                    },
                    {
                        "speaker": "Driver",
                        "text": "Hey Tim, yeah, go ahead.",
                        "timestamp": "2024-01-01T12:00:01.000000"
                    }
                ],
                "audioUrl": None
            }
        }

