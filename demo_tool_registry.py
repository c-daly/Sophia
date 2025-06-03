#!/usr/bin/env python3
"""
Demo script showcasing the Dynamic Tool Registry functionality.

This script demonstrates:
1. Automatic tool discovery through decorators
2. Hot-swapping of tools
3. Tool metadata collection
4. Integration with AgentLoop
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.registry import get_registry, register_tool
from agents.agent_loop import AgentLoop
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, AgentAction, ToolCall
from unittest.mock import MagicMock


def demo_basic_registry():
    """Demonstrate basic registry functionality."""
    print("=== Basic Tool Registry Demo ===\n")
    
    registry = get_registry()
    
    # Show initially registered tools (from imports)
    print("Initially registered tools:")
    for tool_name in registry.list_tools():
        metadata = registry.get_metadata(tool_name)
        print(f"  - {tool_name}: {metadata.description}")
    
    print(f"\nTotal tools: {len(registry.list_tools())}")
    
    # Test calculator tool
    calc_tool = registry.get_tool('calculator')
    if calc_tool:
        print(f"\nTesting calculator: 2 + 2 = {calc_tool('2 + 2')}")
        print(f"Testing calculator: 10 / 3 = {calc_tool('10 / 3'):.2f}")


def demo_decorator_registration():
    """Demonstrate decorator-based tool registration."""
    print("\n=== Decorator Registration Demo ===\n")
    
    registry = get_registry()
    
    # Register a new tool using decorator
    @register_tool(
        name="string_reverser",
        description="Reverses a string",
        tags=["text", "utility"],
        version="1.0.0"
    )
    def reverse_string(text: str) -> str:
        """Reverse the input string."""
        return text[::-1]
    
    # Register another tool
    @register_tool(
        description="Counts words in a text",
        tags=["text", "analysis"]
    )
    def word_counter(text: str) -> int:
        """Count the number of words in the text."""
        return len(text.split())
    
    print("Newly registered tools:")
    for tool_name in ["string_reverser", "word_counter"]:
        if registry.has_tool(tool_name):
            metadata = registry.get_metadata(tool_name)
            print(f"  - {tool_name}: {metadata.description}")
            print(f"    Tags: {metadata.tags}")
            print(f"    Parameters: {list(metadata.parameters.keys())}")
    
    # Test the tools
    print("\nTesting new tools:")
    print(f"Reverse 'hello world': '{reverse_string('hello world')}'")
    print(f"Word count of 'hello world test': {word_counter('hello world test')}")


def demo_hot_swapping():
    """Demonstrate hot-swapping functionality."""
    print("\n=== Hot-Swapping Demo ===\n")
    
    registry = get_registry()
    
    # Original implementation
    @register_tool(name="greeter")
    def original_greeter(name: str) -> str:
        return f"Hello, {name}!"
    
    print("Original greeter:")
    print(f"  {original_greeter('Alice')}")
    
    # Hot-swap with new implementation
    def enhanced_greeter(name: str) -> str:
        return f"Greetings and salutations, {name}! Welcome!"
    
    success = registry.hot_swap("greeter", enhanced_greeter)
    print(f"\nHot-swap successful: {success}")
    
    # Test swapped implementation
    swapped_tool = registry.get_tool("greeter")
    print("Enhanced greeter:")
    print(f"  {swapped_tool('Alice')}")


def demo_metadata_and_filtering():
    """Demonstrate metadata collection and filtering."""
    print("\n=== Metadata and Filtering Demo ===\n")
    
    registry = get_registry()
    
    # Show all tools with metadata
    print("All tools with metadata:")
    metadata_dict = registry.list_tools_with_metadata()
    for tool_name, metadata in metadata_dict.items():
        print(f"  {tool_name}:")
        print(f"    Description: {metadata['description']}")
        print(f"    Tags: {metadata['tags']}")
        print(f"    Version: {metadata['version']}")
        print()
    
    # Filter by tags
    print("Tools tagged with 'text':")
    text_tools = registry.get_tools_by_tag("text")
    for tool_name in text_tools:
        metadata = registry.get_metadata(tool_name)
        print(f"  - {tool_name}: {metadata.description}")


def demo_agent_loop_integration():
    """Demonstrate integration with AgentLoop."""
    print("\n=== AgentLoop Integration Demo ===\n")
    
    # Create a mock agent that always calls a tool
    mock_agent = MagicMock()
    
    # Set up the agent to return a tool call
    mock_state = AgentState()
    tool_call = ToolCall(name="calculator", parameters={"expression": "5 * 6"})
    mock_state.next_action = AgentAction.tool_call(tool_call)
    mock_response = AgentResponse(state=mock_state, output="I need to calculate something", is_done=False)
    mock_agent.step.return_value = mock_response
    
    # Create AgentLoop with dynamic registry
    agent_loop = AgentLoop(mock_agent)
    
    print("Available tools in AgentLoop:")
    for tool_name in agent_loop.get_available_tools():
        print(f"  - {tool_name}")
    
    # Simulate tool execution
    print("\nExecuting tool call: calculator('5 * 6')")
    result = agent_loop.run_single_step(mock_state)
    
    if result.state.history:
        last_message = result.state.history[-1]
        print(f"Tool result: {last_message.content}")
    
    # Show tool metadata from AgentLoop
    print("\nTool metadata from AgentLoop:")
    metadata = agent_loop.get_tool_metadata()
    for tool_name in ["calculator", "web_search"]:
        if tool_name in metadata:
            print(f"  {tool_name}: {metadata[tool_name]['description']}")


def main():
    """Run all demos."""
    print("Dynamic Tool Registry Demonstration")
    print("=" * 40)
    
    try:
        demo_basic_registry()
        demo_decorator_registration()
        demo_hot_swapping()
        demo_metadata_and_filtering()
        demo_agent_loop_integration()
        
        print("\n=== Demo Complete ===")
        print("The dynamic tool registry provides:")
        print("✓ Automatic tool discovery through decorators")
        print("✓ Hot-swapping of tool implementations")
        print("✓ Rich metadata collection and querying")
        print("✓ Thread-safe operations")
        print("✓ Seamless integration with AgentLoop")
        print("✓ Backward compatibility with legacy tools")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()