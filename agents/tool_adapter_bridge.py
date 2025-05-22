"""
Tool adapter bridge for connecting existing tools to the stateful agent framework.

This module provides an adapter that allows existing tools built with the
AbstractTool interface to be used with the stateful agent framework.
"""

from typing import Dict, Any, Optional

from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, AgentAction, ActionType
from tools.abstract_tool import AbstractTool


class ToolAdapterBridge(AbstractAgent):
    """
    A bridge adapter that wraps an AbstractTool to be used as an AbstractAgent.
    
    This enables existing tools to be used with the new stateful agent framework
    without modifying the original tool implementations.
    """
    
    def __init__(self, tool: AbstractTool):
        """
        Initialize the tool adapter.
        
        Args:
            tool: The AbstractTool instance to wrap
        """
        self.tool = tool
        
    def start(self, input_content: str, **metadata) -> AgentResponse:
        """
        Start the tool execution.
        
        Args:
            input_content: The input content to process
            metadata: Additional metadata
            
        Returns:
            An AgentResponse with the execution result
        """
        # Create a new state
        state = AgentState()
        state.add_message("user", input_content)
        state.input = AgentInput(content=input_content, metadata=metadata)
        
        # Process the input immediately
        return self.step(state)
    
    def step(self, state: AgentState) -> AgentResponse:
        """
        Execute the tool with the given input.
        
        Args:
            state: The current state
            
        Returns:
            An AgentResponse with the result of the tool execution
        """
        try:
            # Execute the tool with the input content
            result = self.tool.run(state.input.content)
            result_str = str(result)
            
            # Update the state with the result
            state.add_message("tool", result_str)
            state.next_action = AgentAction(
                type=ActionType.RESPOND,
                content=result_str
            )
            
            return AgentResponse(
                state=state,
                output=result_str,
                is_done=True  # Tool execution is complete after one step
            )
            
        except Exception as e:
            error_message = f"Error executing {self.tool.get_name()}: {str(e)}"
            state.add_message("system", error_message)
            
            return AgentResponse(
                state=state,
                output=error_message,
                is_done=True
            )
    
    def generate_query_sequence(self, text):
        """
        Legacy method for compatibility with the old agent interface.
        
        Args:
            text: The input text
            
        Returns:
            The result of tool execution
        """
        return self.tool.run(text)