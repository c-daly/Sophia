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
    AgentState, AgentInput, AgentResponse, AgentAction, ActionType, Message
)
from agents.tool_agent import ToolAgent, calculator_tool


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


if __name__ == "__main__":
    unittest.main()