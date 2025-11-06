"""
Shared conversation state for both dispatcher and driver agents.

This module provides a shared state mechanism that both agents can access
to coordinate conversation conclusion and disconnection, plus maintain
conversation history so agents can listen to each other properly.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ConversationState:
    """Thread-safe shared conversation state with conversation history."""
    
    def __init__(self):
        self._state = {
            "concluded": False,
            "dispatcher_session": None,
            "driver_session": None,
            "room": None,
            "lock": asyncio.Lock(),
            # NEW: Conversation history to share context between agents
            "messages": [],  # List of {"speaker": "dispatcher|driver", "message": str}
        }
    
    async def reset(self):
        """Reset conversation state for a new conversation."""
        async with self._state.get("lock", asyncio.Lock()):
            self._state["concluded"] = False
            self._state["dispatcher_session"] = None
            self._state["driver_session"] = None
            self._state["room"] = None
            self._state["messages"] = []
    
    async def set_concluded(self, value: bool):
        """Set conversation as concluded."""
        async with self._state.get("lock", asyncio.Lock()):
            self._state["concluded"] = value
    
    async def is_concluded(self) -> bool:
        """Check if conversation is concluded."""
        async with self._state.get("lock", asyncio.Lock()):
            return self._state["concluded"]
    
    async def set_dispatcher_session(self, session):
        """Store dispatcher session."""
        async with self._state.get("lock", asyncio.Lock()):
            self._state["dispatcher_session"] = session
    
    async def set_driver_session(self, session):
        """Store driver session."""
        async with self._state.get("lock", asyncio.Lock()):
            self._state["driver_session"] = session
    
    async def get_dispatcher_session(self):
        """Get dispatcher session."""
        async with self._state.get("lock", asyncio.Lock()):
            return self._state["dispatcher_session"]
    
    async def get_driver_session(self):
        """Get driver session."""
        async with self._state.get("lock", asyncio.Lock()):
            return self._state["driver_session"]
    
    async def set_room(self, room):
        """Store room reference."""
        async with self._state.get("lock", asyncio.Lock()):
            self._state["room"] = room
    
    async def get_room(self):
        """Get room reference."""
        async with self._state.get("lock", asyncio.Lock()):
            return self._state["room"]
    
    # NEW: Message/conversation history methods
    async def add_message(self, speaker: str, message: str):
        """Add a message to conversation history."""
        async with self._state.get("lock", asyncio.Lock()):
            self._state["messages"].append({
                "speaker": speaker,
                "message": message
            })
            logger.debug(f"[Conversation] {speaker}: {message[:100]}")
    
    async def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation so far."""
        async with self._state.get("lock", asyncio.Lock()):
            return self._state["messages"].copy()
    
    async def get_last_messages(self, count: int = 5) -> List[Dict[str, str]]:
        """Get the last N messages for context."""
        async with self._state.get("lock", asyncio.Lock()):
            return self._state["messages"][-count:] if self._state["messages"] else []
    
    async def format_conversation_context(self) -> str:
        """Format conversation history for agent context."""
        async with self._state.get("lock", asyncio.Lock()):
            if not self._state["messages"]:
                return "No previous messages in this conversation yet."
            
            formatted = "Previous conversation:\n"
            for msg in self._state["messages"]:
                formatted += f"- {msg['speaker']}: {msg['message']}\n"
            return formatted
    
    async def disconnect_all(self):
        """Disconnect both agents."""
        async with self._state.get("lock", asyncio.Lock()):
            if self._state["dispatcher_session"]:
                try:
                    await self._state["dispatcher_session"].aclose()
                except:
                    pass
            if self._state["driver_session"]:
                try:
                    await self._state["driver_session"].aclose()
                except:
                    pass
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state (for debugging)."""
        return {
            "concluded": self._state["concluded"],
            "has_dispatcher": self._state["dispatcher_session"] is not None,
            "has_driver": self._state["driver_session"] is not None,
            "has_room": self._state["room"] is not None,
            "message_count": len(self._state["messages"])
        }


# Global shared state instance
_shared_state = ConversationState()


def get_shared_state() -> ConversationState:
    """Get the global shared conversation state."""
    return _shared_state

