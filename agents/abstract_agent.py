from abc import ABC, abstractmethod
from communication.generic_response import GenericResponse
from typing import Optional, Dict, Any, List, Union

from agents.agent_interfaces import AgentState, AgentInput, AgentResponse


# Abstract base class for an agent
class AbstractAgent(ABC):
   
    @abstractmethod
    def start(self, input_content: str, **metadata) -> GenericResponse:
        """
        Start a new agent session with the given input.
        
        Args:
            input_content: The initial input content
            metadata: Additional metadata for the input
            
        Returns:
            An AgentResponse with the initial state
        """
        pass
    
    @abstractmethod
    def step(self, state: AgentState) -> GenericResponse:
        """
        Process a single step in the agent's lifecycle.
        
        Args:
            state: The current agent state
            
        Returns:
            An AgentResponse with the updated state and any output
        """
        pass
