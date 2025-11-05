"""Conversation Service for orchestrating agent conversations."""
from typing import List, Dict
from datetime import datetime
import os
from langfuse import Langfuse
from .llm_service import LLMService


class ConversationTurn:
    """Represents a single turn in a conversation."""
    
    def __init__(self, speaker: str, text: str):
        """Initialize a conversation turn."""
        self.speaker = speaker
        self.text = text
        self.timestamp = datetime.now()


class ConversationService:
    """Service for generating agent conversations."""
    
    def __init__(self, llm_service: LLMService):
        """Initialize conversation service with LLM service."""
        self.llm_service = llm_service
        
        # Initialize Langfuse for conversation-level tracing
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if langfuse_public_key and langfuse_secret_key:
            self.langfuse = Langfuse(
                public_key=langfuse_public_key,
                secret_key=langfuse_secret_key,
                host=langfuse_host
            )
            self.langfuse_enabled = True
        else:
            self.langfuse = None
            self.langfuse_enabled = False
    
    def _format_scenario(self, scenario: Dict) -> str:
        """Format scenario dictionary into readable text."""
        return f"""
Load ID: {scenario['loadId']}
Load Type: {scenario['loadType']}
Weight: {scenario['weight']} lbs
Pickup: {scenario['pickupLocation']} at {scenario['pickupTime']} ({scenario['pickupType']})
Delivery: {scenario['deliveryLocation']} by {scenario['deliveryDeadline']}
Trailer: {scenario['trailerType']}
Rate: ${scenario['ratePerMile']}/mile (${scenario['totalRate']} total)
Accessorials: {scenario['accessorials']}
Securement: {scenario['securementRequirements']}
TMS Update: {scenario['tmsUpdate']}
"""
    
    def _conversation_to_messages(self, conversation: List[ConversationTurn], speaker: str) -> List[Dict]:
        """
        Convert conversation history to message format for LLM.
        
        Args:
            conversation: List of conversation turns
            speaker: The speaker whose perspective to use ("Dispatcher" or "Driver")
        
        Returns:
            List of message dictionaries with role and content
        """
        messages = []
        for turn in conversation:
            # From the speaker's perspective: their messages are "assistant", others are "user"
            role = "assistant" if turn.speaker == speaker else "user"
            messages.append({"role": role, "content": turn.text})
        return messages
    
    def _is_conversation_complete(self, text: str) -> bool:
        """
        Check if conversation should end based on the text.
        
        Args:
            text: The text to check
        
        Returns:
            True if conversation should end, False otherwise
        """
        text_lower = text.lower()
        end_phrases = [
            "thanks",
            "thank you",
            "talk soon",
            "have a good one",
            "see you",
            "bye",
            "goodbye",
            "sounds good",
            "perfect",
            "will do"
        ]
        
        # Check if message is short and contains ending phrase
        words = text_lower.split()
        if len(words) <= 15:  # Short message
            for phrase in end_phrases:
                if phrase in text_lower:
                    return True
        
        return False
    
    async def generate_conversation(
        self,
        scenario: Dict,
        dispatcher_prompt: str,
        driver_prompt: str,
        max_turns: int = 20
    ) -> List[ConversationTurn]:
        """
        Generate a multi-turn conversation between dispatcher and driver.
        
        Args:
            scenario: Load scenario dictionary
            dispatcher_prompt: System prompt for dispatcher agent
            driver_prompt: System prompt for driver agent
            max_turns: Maximum number of conversation turns
        
        Returns:
            List of conversation turns
        """
        # Create Langfuse trace for the entire conversation
        trace = None
        if self.langfuse_enabled:
            try:
                trace = self.langfuse.trace(
                    name="conversation_generation",
                    metadata={
                        "scenario": scenario.get("loadId"),
                        "max_turns": max_turns
                    }
                )
            except Exception as e:
                print(f"⚠ Langfuse trace creation failed: {e}")
        
        conversation = []
        
        # Format scenario for prompts
        scenario_text = self._format_scenario(scenario)
        
        # Create system prompts
        dispatcher_system = f"""{dispatcher_prompt}

You are having a phone conversation with a driver about a load assignment.
Scenario: {scenario_text}

Keep responses natural, brief, and conversational. Don't include stage directions.
"""
        
        driver_system = f"""{driver_prompt}

You are having a phone conversation with a dispatcher about a load assignment.
Scenario: {scenario_text}

Keep responses natural, brief, and conversational. Don't include stage directions.
Respond appropriately to what the dispatcher says.
"""
        
        # Generate dispatcher opening
        dispatcher_message = await self.llm_service.generate_response(
            [
                {"role": "system", "content": dispatcher_system},
                {"role": "user", "content": "Start the conversation with a friendly greeting."}
            ],
            trace_name="dispatcher_opening"
        )
        
        conversation.append(ConversationTurn("Dispatcher", dispatcher_message))
        
        # Initialize message history for dispatcher
        dispatcher_messages = [
            {"role": "system", "content": dispatcher_system},
            {"role": "assistant", "content": dispatcher_message}
        ]
        
        # Generate alternating turns
        for turn_num in range(max_turns):
            # Driver responds
            driver_messages = [
                {"role": "system", "content": driver_system}
            ] + self._conversation_to_messages(conversation, "Driver")
            
            driver_response = await self.llm_service.generate_response(
                driver_messages,
                trace_name=f"driver_turn_{turn_num}"
            )
            conversation.append(ConversationTurn("Driver", driver_response))
            
            # Check if conversation should end
            if self._is_conversation_complete(driver_response):
                break
            
            # Dispatcher responds
            dispatcher_messages.append({"role": "user", "content": driver_response})
            dispatcher_response = await self.llm_service.generate_response(
                dispatcher_messages,
                trace_name=f"dispatcher_turn_{turn_num}"
            )
            conversation.append(ConversationTurn("Dispatcher", dispatcher_response))
            dispatcher_messages.append({"role": "assistant", "content": dispatcher_response})
            
            # Check if conversation should end
            if self._is_conversation_complete(dispatcher_response):
                break
        
        # Update trace with final metadata
        if trace:
            try:
                trace.update(
                    metadata={
                        "total_turns": len(conversation),
                        "completed": True
                    }
                )
            except Exception as e:
                print(f"⚠ Langfuse trace update failed: {e}")
        
        return conversation

