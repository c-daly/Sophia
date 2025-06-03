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
    role: str  # "system", "user", "assistant", "tool", etc.
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInput:
    """Input provided to an agent."""
    content: str  # The primary content (e.g., user's message)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context or parameters


@dataclass
class ToolCall:
    """Specification for a tool to be called."""
    name: str  # Name of the tool
    parameters: Dict[str, Any] = field(default_factory=dict)  # Parameters for the tool call


@dataclass
class AgentAction:
    """
    Action determined by the agent to take next.
    
    The payload dict contains action-specific data:
    - For RESPOND actions: {"content": str} - The response content
    - For TOOL_CALL actions: {"tool_call": ToolCall} - The tool call specification
    - For DELEGATE actions: {"delegate_to": str} - The name of the agent to delegate to
    - For COMPLETE actions: {} - No additional data required
    - For PENDING actions: {} - No additional data required
    
    The metadata dict can contain any additional contextual information.
    """
    type: ActionType
    payload: Dict[str, Any] = field(default_factory=dict)  # Generic payload for all action types
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context or logging
    
    @classmethod
    def respond(cls, content: str, **metadata) -> 'AgentAction':
        """
        Create a RESPOND action.
        
        Args:
            content: The response content
            metadata: Optional metadata
            
        Returns:
            An AgentAction of type RESPOND
        """
        return cls(
            type=ActionType.RESPOND,
            payload={"content": content},
            metadata=metadata
        )
    
    @classmethod
    def tool_call(cls, tool_call: ToolCall, **metadata) -> 'AgentAction':
        """
        Create a TOOL_CALL action.
        
        Args:
            tool_call: The tool call specification
            metadata: Optional metadata
            
        Returns:
            An AgentAction of type TOOL_CALL
        """
        return cls(
            type=ActionType.TOOL_CALL,
            payload={"tool_call": tool_call},
            metadata=metadata
        )
    
    @classmethod
    def delegate(cls, agent_name: str, **metadata) -> 'AgentAction':
        """
        Create a DELEGATE action.
        
        Args:
            agent_name: The name of the agent to delegate to
            metadata: Optional metadata
            
        Returns:
            An AgentAction of type DELEGATE
        """
        return cls(
            type=ActionType.DELEGATE,
            payload={"delegate_to": agent_name},
            metadata=metadata
        )
    
    @classmethod
    def complete(cls, **metadata) -> 'AgentAction':
        """
        Create a COMPLETE action.
        
        Args:
            metadata: Optional metadata
            
        Returns:
            An AgentAction of type COMPLETE
        """
        return cls(
            type=ActionType.COMPLETE,
            metadata=metadata
        )
    
    @classmethod
    def pending(cls, **metadata) -> 'AgentAction':
        """
        Create a PENDING action.
        
        Args:
            metadata: Optional metadata
            
        Returns:
            An AgentAction of type PENDING
        """
        return cls(
            type=ActionType.PENDING,
            metadata=metadata
        )
    
    # Properties for backward compatibility
    @property
    def content(self) -> Optional[str]:
        """Get content from payload for backward compatibility."""
        return self.payload.get("content")
    
    @property
    def tool_call_data(self) -> Optional[ToolCall]:
        """Get tool_call from payload for backward compatibility."""
        return self.payload.get("tool_call")
    
    @property
    def delegate_to(self) -> Optional[str]:
        """Get delegate_to from payload for backward compatibility."""
        return self.payload.get("delegate_to")


@dataclass
class AgentState:
    """The current state of an agent's processing."""
    input: Optional[GenericRequest] = None  # Current input being processed
    user_msg: Optional[GenericRequest] = None  # Current input being processed
    history: List[Message] = field(default_factory=list)  # Conversation history
    next_action: AgentAction = field(default_factory=lambda: AgentAction.pending())
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


@dataclass
class AgentResponse:
    """Response from an agent processing step."""
    state: AgentState
    output: Optional[str] = None  # Output text if available
    is_done: bool = False  # Whether the agent has completed its task
