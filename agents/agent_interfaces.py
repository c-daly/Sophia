"""
Core interfaces for stateful agent framework.

This module provides the data structures used for the stateful agent lifecycle, 
including AgentInput, AgentState, and AgentResponse classes.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable
from communication.generic_request import GenericRequest


class ActionType(Enum):
    """Types of actions an agent can take."""
    RESPOND = "respond"  # Generate a response to the user
    TOOL_CALL = "tool_call"  # Call a tool with specific parameters
    DELEGATE = "delegate"  # Delegate to another agent
    COMPLETE = "complete"  # End the conversation
    PENDING = "pending"  # No action determined yet


@dataclass
class Message:
    """A message in the conversation history."""
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentState:
    """The current state of an agent's processing."""
    input: Optional[GenericRequest] = None  # Current input being processed
    history: List[Message] = field(default_factory=list)  # Conversation history
    #next_action: AgentAction = field(default_factory=lambda: AgentAction.pending())
    working_memory: Dict[str, Any] = field(default_factory=dict)  # Agent's working memory
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional state information

    def add_message(self, role: str, content: str, **metadata):
        """Add a message to the conversation history."""
        self.history.append(Message(role=role, content=content, metadata=metadata))

    def get_last_message(self) -> Optional[Message]:
        """Get the most recent message in the history."""
        return self.history[-1] if self.history else None
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Convert history to format expected by LLM APIs."""
        return [{"role": msg.role, "content": msg.content} for msg in self.history]

