# Stateful Agent Framework

## Overview

The Sophia Stateful Agent Framework provides a flexible, extensible architecture for building AI agents with:

1. **Lifecycle management** through `start()` and `step()` methods
2. **State tracking** via the `AgentState` object
3. **Composable design** with unified agent and tool interfaces
4. **Action-based processing** for responding, tool use, and delegation
5. **Dynamic tool registry** for automatic tool discovery and hot-swapping

## Core Components

### Agent Interface

All agents implement the `AbstractAgent` interface which provides:

- `start(input_content, **metadata)`: Initialize a new agent session
- `step(state)`: Process a single turn in the conversation
- `generate_query_sequence(text)`: Legacy method for backward compatibility

### Dynamic Tool Registry

The framework includes a sophisticated tool registry system that provides:

- **Automatic Discovery**: Tools are registered automatically when modules are imported
- **Decorator Pattern**: Use `@register_tool` to mark functions as tools
- **Hot-swapping**: Replace tool implementations at runtime
- **Rich Metadata**: Automatic parameter extraction and tool descriptions
- **Thread Safety**: Concurrent access support

See the [Dynamic Tool Registry](tool_registry.md) documentation for detailed information.

### Data Structures

#### AgentState

Tracks all information about an agent's ongoing session:

```python
state = AgentState(
    input=AgentInput(content="Hello"),
    history=[Message(role="system", content="You are a helpful assistant")],
    next_action=AgentAction(type=ActionType.PENDING),
    working_memory={},
    metadata={}
)
```

Key components:
- `input`: The current input being processed
- `history`: Conversation history as a list of messages
- `next_action`: The next action the agent plans to take
- `working_memory`: Agent's scratch space for temporary data
- `metadata`: Additional context information

#### AgentAction

Represents the next action an agent plans to take:

```python
# Using helper methods (recommended)
action = AgentAction.respond("I'll help you with that.")

# Or directly with payload
action = AgentAction(
    type=ActionType.RESPOND,
    payload={"content": "I'll help you with that."}
)
```

Action types and their expected payload structure:
- `RESPOND`: `{"content": str}` - Generate a text response
- `TOOL_CALL`: `{"tool_call": ToolCall}` - Execute a tool
- `DELEGATE`: `{"delegate_to": str}` - Hand off to another agent
- `COMPLETE`: `{}` - End the conversation
- `PENDING`: `{}` - No action determined yet

Helper methods are available for creating each type of action:
```python
AgentAction.respond("Hello there")
AgentAction.tool_call(ToolCall(name="calculator", parameters={"expression": "2+2"}))
AgentAction.delegate("math_agent")
AgentAction.complete()
AgentAction.pending()
```

#### AgentResponse

The result of an agent processing step:

```python
response = AgentResponse(
    state=updated_state,
    output="Hello, how can I help you?",
    is_done=False
)
```

## Agent Loop

The `AgentLoop` class manages the execution flow for stateful agents and integrates with the dynamic tool registry:

```python
from agents.agent_loop import AgentLoop
from tools.registry import register_tool

# Register tools using the decorator
@register_tool(name="calculator", description="Performs calculations")
def calculator(expression: str) -> float:
    return eval(expression)

# AgentLoop automatically uses the global tool registry
agent = StatefulConversationalAgent()
loop = AgentLoop(agent)

# Interactive conversation
loop.run_interactive("Hello")

# Single turn processing
response = loop.run_single_step(state)

# Run until completion
final_response = loop.run_until_done("Solve 2+2")

# Access available tools
available_tools = loop.get_available_tools()
tool_metadata = loop.get_tool_metadata()
```

### Legacy Tool Support

For backward compatibility, you can still provide tools via dictionary:

```python
# Legacy approach (still supported)
legacy_tools = {"old_tool": old_tool_function}
loop = AgentLoop(agent, legacy_tool_registry=legacy_tools)
```

## Creating Custom Agents

### Basic Agent Template

```python
class MyCustomAgent(AbstractAgent):
    def __init__(self):
        # Initialize any resources
        pass
        
    def start(self, input_content, **metadata):
        # Create initial state
        state = AgentState()
        state.add_message("system", "System prompt")
        state.add_message("user", input_content)
        state.input = AgentInput(content=input_content, metadata=metadata)
        
        # Process the initial state
        return self.step(state)
        
    def step(self, state):
        # Process the current state
        # ...
        
        # Return the result
        return AgentResponse(
            state=state,
            output="Result",
            is_done=False
        )
        
    def generate_query_sequence(self, text):
        # For backward compatibility
        response = self.start(text)
        return response.output
```

### Converting Tools to Agents

The `ToolAgent` class provides a wrapper to use function-based tools in the agent framework:

```python
def my_tool_function(param1, param2):
    # Tool implementation
    return result

tool_agent = ToolAgent(
    tool_fn=my_tool_function,
    name="MyTool",
    description="Description of what the tool does"
)
```

## Running Agents

### CLI Driver

The included CLI driver demonstrates using agents from the command line:

```bash
# Interactive mode with conversational agent
python cli_driver.py -i -a conversational

# Single response from calculator agent
python cli_driver.py -a calculator "2 + 2"
```

## Migration Path

For existing agents:

1. Keep the `generate_query_sequence` method for backward compatibility
2. Add the new lifecycle methods `start()` and `step()`
3. Convert internal state to use `AgentState`
4. Migrate tools to use the dynamic tool registry with `@register_tool`

### Tool Migration

Convert existing tools to use the new registry:

```python
# Old tool class
class CalculatorTool(AbstractTool):
    def run(self, expression):
        return eval(expression)
    
    def get_name(self):
        return "calculator"

# New registered function
@register_tool(
    name="calculator",
    description="Evaluates mathematical expressions",
    tags=["math", "utility"]
)
def calculator_tool(expression: str) -> float:
    """Safely evaluate a mathematical expression."""
    return eval(expression)
```

## Best Practices

1. Keep agents stateless, with all session data in `AgentState`
2. Use `working_memory` for transient data within a session
3. Design agents to handle a single step at a time
4. Use the dynamic tool registry with `@register_tool` for external functionality
5. Return meaningful output in `AgentResponse`
6. Include comprehensive tool metadata for better discoverability
7. Use tags to categorize tools for easy filtering
8. Implement proper error handling in tools