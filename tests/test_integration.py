"""
Integration tests for the stateful agent framework with components_and_tools.

These tests verify that our stateful agent framework correctly integrates with
the components and tools from the components_and_tools branch.
"""

import unittest
from unittest.mock import MagicMock, patch

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


class TestFrameworkIntegration(unittest.TestCase):
    """Test cases for integration between framework and components_and_tools."""
    
    def test_tool_adapter_bridge(self):
        """Test that ToolAdapterBridge correctly wraps existing tools."""
        # Create a tool
        tool = MockTool(return_value="Test tool result")
        
        # Create the adapter
        adapter = ToolAdapterBridge(tool)
        
        # Test with legacy interface
        legacy_result = adapter.generate_query_sequence("test input")
        self.assertEqual(legacy_result, "Test tool result")
        
        # Test with new interface
        response = adapter.start("test input")
        self.assertEqual(response.output, "Test tool result")


if __name__ == "__main__":
    unittest.main()