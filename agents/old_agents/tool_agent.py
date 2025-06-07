"""
Tool agent implementation.

This module demonstrates how to wrap a simple function-based tool
as a stateful agent, demonstrating the composable agent pattern.
"""

from typing import Dict, Any, Callable, Optional
import re

from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, AgentAction, ActionType


class ToolAgent(AbstractAgent):
    """
    A wrapper for function-based tools to act as agents.
    
    This agent wraps a Python function as an agent, enabling tools to be
    used within the same agent framework as conversational agents.
    """
    
    def __init__(
        self, 
        tool_fn: Callable, 
        name: str, 
        description: str = "",
        input_parser: Optional[Callable[[str], Dict[str, Any]]] = None
    ):
        """
        Initialize the tool agent.
        
        Args:
            tool_fn: The function implementing the tool's functionality
            name: The name of the tool
            description: A description of what the tool does
            input_parser: Optional function to parse text input into parameters
        """
        self.tool_fn = tool_fn
        self.name = name
        self.description = description
        self.input_parser = input_parser or self._default_parser
    
    def _default_parser(self, text: str) -> Dict[str, Any]:
        """
        Default parser that attempts to extract parameters from text.
        
        Args:
            text: The input text
            
        Returns:
            A dictionary of parameter names to values
        """
        # Simple parser that looks for parameter=value patterns
        params = {}
        pattern = r'(\w+)=([^,\s]+)'
        matches = re.findall(pattern, text)
        
        for name, value in matches:
            # Try to convert to appropriate types
            if value.lower() == 'true':
                params[name] = True
            elif value.lower() == 'false':
                params[name] = False
            elif value.isdigit():
                params[name] = int(value)
            elif value.replace('.', '', 1).isdigit() and value.count('.') <= 1:
                params[name] = float(value)
            else:
                params[name] = value
        
        return params
    
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
        Execute the tool function with the given input.
        
        Args:
            state: The current state
            
        Returns:
            An AgentResponse with the result of the tool execution
        """
        try:
            # Parse the input into parameters
            params = self.input_parser(state.input.content)
            
            # Execute the tool function with the parsed parameters
            result = self.tool_fn(**params)
            result_str = str(result)
            
            # Update the state with the result
            state.add_message("tool", result_str)
            state.next_action = AgentAction.respond(result_str)
            
            return AgentResponse(
                state=state,
                output=result_str,
                is_done=True  # Tool execution is complete after one step
            )
            
        except Exception as e:
            error_message = f"Error executing {self.name}: {str(e)}"
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
        response = self.start(text)
        return response.output


# Example calculator tool implementation
def calculator_tool(expression: str) -> float:
    """
    A simple calculator tool that evaluates mathematical expressions.
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        The result of evaluating the expression
    """
    # Remove any potentially dangerous operations
    safe_expr = re.sub(r'[^0-9+\-*/().%\s]', '', expression)
    
    try:
        return eval(safe_expr)
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}")


# Example of creating a calculator agent
def create_calculator_agent():
    """
    Create a calculator tool agent.
    
    Returns:
        A ToolAgent that performs calculations
    """
    def calculator_parser(text: str) -> Dict[str, Any]:
        """Extract the expression from input text."""
        # Look for explicit parameter
        match = re.search(r'expression=([^,\s]+)', text)
        if match:
            return {"expression": match.group(1)}
        
        # Otherwise treat the whole text as the expression
        return {"expression": text}
    
    return ToolAgent(
        tool_fn=calculator_tool,
        name="Calculator",
        description="Evaluates simple mathematical expressions",
        input_parser=calculator_parser
    )