"""
Tests for the stateful agent framework.

This module contains unit tests for the stateful agent framework components.
"""

import unittest
import sys
from unittest.mock import patch, MagicMock

# Mock config and other dependencies
sys.modules['config'] = MagicMock()
sys.modules['models.static_openai_wrapper'] = MagicMock()
sys.modules['data.mongo_wrapper'] = MagicMock()
sys.modules['data.milvus_wrapper'] = MagicMock()
sys.modules['prompts.prompts'] = MagicMock(DEFAULT_PROMPT="You are a helpful assistant")

from agents.agent_interfaces import (
    AgentState, AgentAction, ActionType, ToolCall
)

from agents.tool_agent import ToolAgent, calculator_tool
from agents.agent_loop import AgentLoop
from tools.registry import get_registry


class TestAgentInterfaces(unittest.TestCase):
    """Tests for the agent interface classes."""
    
    def test_agent_state(self):
        """Test AgentState functionality."""
        state = AgentState()
        state.add_message("system", "System prompt")
        state.add_message("user", "User message")
        
        self.assertEqual(len(state.history), 2)
        self.assertEqual(state.history[0].role, "system")
        self.assertEqual(state.history[1].content, "User message")
        
        messages_for_llm = state.get_messages_for_llm()
        self.assertEqual(len(messages_for_llm), 2)
        self.assertEqual(messages_for_llm[0]["role"], "system")
        self.assertEqual(messages_for_llm[1]["content"], "User message")
        
        last_msg = state.get_last_message()
        self.assertEqual(last_msg.role, "user")
        self.assertEqual(last_msg.content, "User message")
    
    def test_agent_action_respond(self):
        """Test AgentAction.respond helper method."""
        action = AgentAction.respond("Hello, world!")
        self.assertEqual(action.type, ActionType.RESPOND)
        self.assertEqual(action.payload["content"], "Hello, world!")
        self.assertEqual(action.metadata, {})
        
        # With metadata
        action = AgentAction.respond("Hello, world!", source="user-query")
        self.assertEqual(action.metadata["source"], "user-query")
    
    def test_agent_action_tool_call(self):
        """Test AgentAction.tool_call helper method."""
        tool_call = ToolCall(name="calculator", parameters={"expression": "2+2"})
        action = AgentAction.tool_call(tool_call)
        self.assertEqual(action.type, ActionType.TOOL_CALL)
        self.assertEqual(action.payload["tool_call"], tool_call)
        
    def test_agent_action_delegate(self):
        """Test AgentAction.delegate helper method."""
        action = AgentAction.delegate("math_agent")
        self.assertEqual(action.type, ActionType.DELEGATE)
        self.assertEqual(action.payload["delegate_to"], "math_agent")
        
    def test_agent_action_complete(self):
        """Test AgentAction.complete helper method."""
        action = AgentAction.complete()
        self.assertEqual(action.type, ActionType.COMPLETE)
        self.assertEqual(action.payload, {})
        
    def test_agent_action_pending(self):
        """Test AgentAction.pending helper method."""
        action = AgentAction.pending()
        self.assertEqual(action.type, ActionType.PENDING)
        self.assertEqual(action.payload, {})
    
    def test_agent_action_backward_compatibility(self):
        """Test backward compatibility of AgentAction payload with old attributes."""
        # Create action using the new payload approach
        action = AgentAction.respond("Hello, world!")
        
        # Verify that the payload is accessible directly via attribute access
        # This ensures backward compatibility with code that expects direct attributes
        self.assertEqual(action.content, "Hello, world!")
        self.assertEqual(action.payload["content"], "Hello, world!")
        
        # Test tool_call
        tool_call = ToolCall(name="calculator", parameters={"expression": "2+2"})
        action = AgentAction.tool_call(tool_call)
        self.assertEqual(action.tool_call_data, tool_call)
        self.assertEqual(action.payload["tool_call"], tool_call)
        
        # Test delegate
        action = AgentAction.delegate("math_agent")
        self.assertEqual(action.delegate_to, "math_agent")
        self.assertEqual(action.payload["delegate_to"], "math_agent")


class TestToolFunctionality(unittest.TestCase):
    """Tests for the tool functionality."""
    
    def test_calculator_function(self):
        """Test the calculator tool function directly."""
        # Test basic arithmetic
        result = calculator_tool("2 + 2")
        self.assertEqual(result, 4)
        
        # Test multiplication
        result = calculator_tool("3 * 5")
        self.assertEqual(result, 15)
        
        # Test division
        result = calculator_tool("10 / 2")
        self.assertEqual(result, 5.0)
        
        # Test with whitespace
        result = calculator_tool(" 7 - 3 ")
        self.assertEqual(result, 4)


class TestAgentLoopWithToolRegistry(unittest.TestCase):
    """Tests for AgentLoop integration with the dynamic tool registry."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the registry before each test
        self.registry = get_registry()
        self.registry.clear()
        
        # Create a mock agent for testing
        self.mock_agent = MagicMock()
        self.agent_loop = AgentLoop(self.mock_agent)
    
    def test_agent_loop_uses_dynamic_registry(self):
        """Test that AgentLoop can use tools from the dynamic registry."""
        # Register a test tool
        def test_tool(message: str) -> str:
            return f"Tool response: {message}"
        
        self.registry.register("test_tool", test_tool, "A test tool")
        
        # Check that the tool is available
        self.assertIn("test_tool", self.agent_loop.get_available_tools())
        
        # Verify tool metadata
        metadata = self.agent_loop.get_tool_metadata()
        self.assertIn("test_tool", metadata)
        self.assertEqual(metadata["test_tool"]["description"], "A test tool")
    
    def test_agent_loop_tool_execution(self):
        """Test that AgentLoop can execute tools properly."""
        # Register a simple tool
        def echo_tool(message: str) -> str:
            return f"Echo: {message}"
        
        self.registry.register("echo", echo_tool)
        
        # Create a mock agent response with a tool call
        mock_state = AgentState()
        tool_call = ToolCall(name="echo", parameters={"message": "hello"})
        mock_state.next_action = AgentAction.tool_call(tool_call)
        
        mock_response = AgentResponse(state=mock_state, output="", is_done=False)
        self.mock_agent.step.return_value = mock_response
        
        # Execute the step
        result = self.agent_loop.run_single_step(mock_state)
        
        # Verify tool was executed and result was added to history
        self.assertEqual(len(result.state.history), 1)
        self.assertEqual(result.state.history[0].role, "tool")
        self.assertEqual(result.state.history[0].content, "Echo: hello")
    
    def test_agent_loop_tool_error_handling(self):
        """Test that AgentLoop handles tool errors gracefully."""
        # Register a tool that raises an error
        def error_tool() -> str:
            raise ValueError("Tool error")
        
        self.registry.register("error_tool", error_tool)
        
        # Create a mock agent response with a tool call
        mock_state = AgentState()
        tool_call = ToolCall(name="error_tool", parameters={})
        mock_state.next_action = AgentAction.tool_call(tool_call)
        
        mock_response = AgentResponse(state=mock_state, output="", is_done=False)
        self.mock_agent.step.return_value = mock_response
        
        # Execute the step
        result = self.agent_loop.run_single_step(mock_state)
        
        # Verify error was handled
        self.assertEqual(len(result.state.history), 1)
        self.assertEqual(result.state.history[0].role, "system")
        self.assertIn("Error executing tool error_tool", result.state.history[0].content)
    
    def test_agent_loop_missing_tool_handling(self):
        """Test that AgentLoop handles missing tools gracefully."""
        # Create a mock agent response with a tool call for non-existent tool
        mock_state = AgentState()
        tool_call = ToolCall(name="nonexistent_tool", parameters={})
        mock_state.next_action = AgentAction.tool_call(tool_call)
        
        mock_response = AgentResponse(state=mock_state, output="", is_done=False)
        self.mock_agent.step.return_value = mock_response
        
        # Execute the step
        result = self.agent_loop.run_single_step(mock_state)
        
        # Verify error was handled
        self.assertEqual(len(result.state.history), 1)
        self.assertEqual(result.state.history[0].role, "system")
        self.assertIn("Tool 'nonexistent_tool' not found", result.state.history[0].content)


if __name__ == "__main__":
    unittest.main()
