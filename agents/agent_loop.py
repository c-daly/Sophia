"""
Agent loop runner for stateful agent framework.

This module provides utilities for running agents in a turn-by-turn interactive loop,
handling the execution of agent actions and managing the conversation flow.
"""

from typing import Dict, Any, Optional, Callable, List
import time

from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, ActionType, ToolCall
from tools.registry import ToolRegistry, get_registry


class AgentLoop:
    """
    A loop runner for agents using the stateful framework.
    
    This class handles the execution of agents through their lifecycle,
    processing input, executing actions, and managing the conversation flow.
    """
    
    def __init__(
        self, 
        agent: AbstractAgent,
        tool_registry: Optional[ToolRegistry] = None,
        legacy_tool_registry: Optional[Dict[str, Callable]] = None,
        max_turns: int = 10
    ):
        """
        Initialize the agent loop.
        
        Args:
            agent: The agent to run in this loop
            tool_registry: A ToolRegistry instance (uses global registry if None)
            legacy_tool_registry: A mapping of tool names to functions (for backward compatibility)
            max_turns: Maximum number of turns to prevent infinite loops
        """
        self.agent = agent
        self.tool_registry = tool_registry or get_registry()
        self.legacy_tool_registry = legacy_tool_registry or {}
        self.max_turns = max_turns
    
    def start(self, input_content: str, **metadata) -> AgentResponse:
        """
        Start a new agent session.
        
        Args:
            input_content: The initial input content
            metadata: Additional metadata for the input
            
        Returns:
            The agent's response after starting
        """
        return self.agent.start(input_content, **metadata)
    
    def run_single_step(self, state: AgentState) -> AgentResponse:
        """
        Run a single step of the agent's lifecycle and process any resulting actions.
        
        Args:
            state: The current agent state
            
        Returns:
            The updated agent response
        """
        # Have the agent process the current state
        response = self.agent.step(state)
        
        # Process any actions the agent determined to take
        if response.state.next_action.type == ActionType.TOOL_CALL and "tool_call" in response.state.next_action.payload:
            # Execute the tool call
            tool_call = response.state.next_action.payload["tool_call"]
            tool_name = tool_call.name
            
            # First try the dynamic registry
            tool_function = self.tool_registry.get_tool(tool_name)
            
            # Fall back to legacy registry for backward compatibility
            if tool_function is None and tool_name in self.legacy_tool_registry:
                tool_function = self.legacy_tool_registry[tool_name]
            
            if tool_function is not None:
                try:
                    result = tool_function(**tool_call.parameters)
                    # Record the tool result in history
                    response.state.add_message("tool", str(result))
                    # Update the input for the next step
                    response.state.input = AgentInput(
                        content=str(result),
                        metadata={"tool_name": tool_name}
                    )
                except Exception as e:
                    error_message = f"Error executing tool {tool_name}: {str(e)}"
                    response.state.add_message("system", error_message)
                    response.state.input = AgentInput(
                        content=error_message,
                        metadata={"error": True}
                    )
            else:
                error_message = f"Tool '{tool_name}' not found in the tool registry"
                response.state.add_message("system", error_message)
                response.state.input = AgentInput(
                    content=error_message,
                    metadata={"error": True}
                )
        
        return response
    
    def run_until_done(self, input_content: str, **metadata) -> AgentResponse:
        """
        Run the agent until it completes or reaches the maximum number of turns.
        
        Args:
            input_content: The initial input content
            metadata: Additional metadata for the input
            
        Returns:
            The final agent response
        """
        # Start the agent session
        response = self.start(input_content, **metadata)
        
        # Run until the agent is done or we reach max_turns
        turn_count = 0
        while not response.is_done and turn_count < self.max_turns:
            response = self.run_single_step(response.state)
            turn_count += 1
            
            # If we've reached max turns but the agent isn't done, mark it as done
            if turn_count >= self.max_turns and not response.is_done:
                response.state.add_message(
                    "system", 
                    f"Agent execution stopped after reaching maximum of {self.max_turns} turns."
                )
                response.is_done = True
        
        return response
    
    def run_interactive(self, initial_input: str) -> None:
        """
        Run the agent in an interactive mode, accepting user input after each step.
        
        Args:
            initial_input: The initial input to start the conversation
        """
        # Start the agent session
        response = self.start(initial_input)
        print(f"Agent: {response.output}")
        
        # Continue interaction until the agent is done or we hit max_turns
        turn_count = 0
        while not response.is_done and turn_count < self.max_turns:
            # Get user input
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Ending conversation.")
                break
            
            # Add the user input to the conversation history
            response.state.add_message("user", user_input)
            response.state.input = AgentInput(content=user_input)
            
            # Run the agent step
            response = self.run_single_step(response.state)
            print(f"Agent: {response.output}")
            
            turn_count += 1

    def get_available_tools(self) -> List[str]:
        """
        Get a list of all available tools.
        
        Returns:
            List of tool names from both dynamic and legacy registries
        """
        dynamic_tools = self.tool_registry.list_tools()
        legacy_tools = list(self.legacy_tool_registry.keys())
        return dynamic_tools + [tool for tool in legacy_tools if tool not in dynamic_tools]
    
    def get_tool_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all available tools.
        
        Returns:
            Dictionary mapping tool names to their metadata
        """
        metadata = self.tool_registry.list_tools_with_metadata()
        
        # Add legacy tools with basic metadata
        for tool_name, tool_func in self.legacy_tool_registry.items():
            if tool_name not in metadata:
                metadata[tool_name] = {
                    "name": tool_name,
                    "description": getattr(tool_func, '__doc__', '') or f"Legacy tool: {tool_name}",
                    "parameters": {},
                    "tags": ["legacy"],
                    "version": "unknown",
                    "module": getattr(tool_func, '__module__', '')
                }
        
        return metadata
    
    def register_legacy_tool(self, name: str, function: Callable):
        """
        Register a tool using the legacy interface.
        
        Args:
            name: Tool name
            function: Tool function
        """
        self.legacy_tool_registry[name] = function
