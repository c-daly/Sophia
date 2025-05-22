"""
Tests for the ToolAdapterBridge.

These tests verify that the bridge adapter correctly connects
existing AbstractTool implementations to the stateful agent framework.
"""

import unittest
from unittest.mock import MagicMock

from agents.tool_adapter_bridge import ToolAdapterBridge
from tools.abstract_tool import AbstractTool


class MockTool(AbstractTool):
    """A mock implementation of AbstractTool for testing."""
    
    def __init__(self, name="MockTool", return_value="Mock result"):
        self.name = name
        self.return_value = return_value
    
    def run(self, args=None):
        return self.return_value
    
    def get_name(self):
        return self.name


class TestToolAdapterBridge(unittest.TestCase):
    """Test cases for the ToolAdapterBridge."""
    
    def test_start_method(self):
        """Test that start() properly initializes the state and calls step()."""
        # Create a mock tool
        mock_tool = MockTool(return_value="Test result")
        
        # Create the adapter
        adapter = ToolAdapterBridge(mock_tool)
        
        # Call start
        response = adapter.start("test input")
        
        # Check response
        self.assertEqual(response.output, "Test result")
        self.assertTrue(response.is_done)
        
        # Check state
        self.assertEqual(len(response.state.history), 2)  # user message + tool response
        self.assertEqual(response.state.history[0].role, "user")
        self.assertEqual(response.state.history[0].content, "test input")
        self.assertEqual(response.state.history[1].role, "tool")
        self.assertEqual(response.state.history[1].content, "Test result")
    
    def test_step_method(self):
        """Test that step() calls the tool's run method and returns the result."""
        # Create a real tool with a mock run method
        tool = MockTool()
        tool.run = MagicMock(return_value="Mocked result")
        
        # Create the adapter
        adapter = ToolAdapterBridge(tool)
        
        # Create a state with fresh input (don't use start method)
        from agents.agent_interfaces import AgentState, AgentInput
        state = AgentState()
        state.input = AgentInput(content="test input")
        
        # Call step
        response = adapter.step(state)
        
        # Check that the tool's run method was called
        tool.run.assert_called_once_with("test input")
        
        # Check response
        self.assertEqual(response.output, "Mocked result")
        self.assertTrue(response.is_done)
    
    def test_error_handling(self):
        """Test that errors from the tool are properly handled."""
        # Create a tool that raises an exception
        tool = MockTool()
        tool.run = MagicMock(side_effect=ValueError("Test error"))
        
        # Create the adapter
        adapter = ToolAdapterBridge(tool)
        
        # Call start
        response = adapter.start("test input")
        
        # Check response indicates an error
        self.assertIn("Error executing", response.output)
        self.assertIn("Test error", response.output)
        self.assertTrue(response.is_done)
    
    def test_generate_query_sequence(self):
        """Test the legacy compatibility method."""
        # Create a mock tool
        mock_tool = MockTool(return_value="Legacy result")
        
        # Create the adapter
        adapter = ToolAdapterBridge(mock_tool)
        
        # Test the legacy method
        result = adapter.generate_query_sequence("legacy input")
        self.assertEqual(result, "Legacy result")


if __name__ == "__main__":
    unittest.main()