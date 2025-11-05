"""Conversation API routes."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
from ...models.schemas import (
    ConversationRequest,
    ConversationResponse,
    ConversationTurn as ConversationTurnSchema
)
from ...services.llm_service import LLMService
from ...services.conversation_service import ConversationService

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("/generate", response_model=ConversationResponse)
async def generate_conversation(request: ConversationRequest):
    """
    Generate a conversation between dispatcher and driver agents.
    
    Uses OpenRouter API for LLM calls and Langfuse for observability.
    """
    try:
        # Get API key from environment
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENROUTER_API_KEY not configured on server"
            )
        
        # Initialize services
        llm_service = LLMService(api_key=api_key)
        conversation_service = ConversationService(llm_service)
        
        # Generate conversation
        conversation_turns = await conversation_service.generate_conversation(
            scenario=request.scenario.model_dump(),
            dispatcher_prompt=request.dispatcherAgent.prompt,
            driver_prompt=request.driverAgent.prompt,
            max_turns=20
        )
        
        # Convert to response format
        transcript = [
            ConversationTurnSchema(
                speaker=turn.speaker,
                text=turn.text,
                timestamp=turn.timestamp.isoformat()
            )
            for turn in conversation_turns
        ]
        
        return ConversationResponse(
            conversationId=datetime.now().isoformat(),
            transcript=transcript,
            audioUrl=None  # Will be implemented in later milestones
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating conversation: {str(e)}"
        )

