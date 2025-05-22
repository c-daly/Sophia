# Stateful Agent Framework

## Overview

The Sophia Stateful Agent Framework provides a flexible, extensible architecture for building AI agents with:

1. **Lifecycle management** through `start()` and `step()` methods
2. **State tracking** via the `AgentState` object
3. **Composable design** with unified agent and tool interfaces
4. **Action-based processing** for responding, tool use, and delegation

## Core Components

### Agent Interface

All agents implement the `AbstractAgent` interface which provides:

- `start(input_content, **metadata)`: Initialize a new agent session
- `step(state)`: Process a single turn in the conversation
- `generate_query_sequence(text)`: Legacy method for backward compatibility

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
action = AgentAction(
    type=ActionType.RESPOND,
    content="I'll help you with that."
)
```

Action types include:
- `RESPOND`: Generate a text response
- `TOOL_CALL`: Execute a tool
- `DELEGATE`: Hand off to another agent
- `COMPLETE`: End the conversation
- `PENDING`: No action determined yet

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

The `AgentLoop` class manages the execution flow for stateful agents:

```python
agent = StatefulConversationalAgent()
loop = AgentLoop(agent, tool_registry={"calculator": calculator_fn})

# Interactive conversation
loop.run_interactive("Hello")

# Single turn processing
response = loop.run_single_step(state)

# Run until completion
final_response = loop.run_until_done("Solve 2+2")
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

### Using Existing AbstractTool Implementations

The `ToolAdapterBridge` provides compatibility with existing tools that implement the `AbstractTool` interface:

```python
from tools.web_search_tool import WebSearchTool
from agents.tool_adapter_bridge import ToolAdapterBridge

# Create the original tool
web_search_tool = WebSearchTool()

# Wrap it as a stateful agent
web_search_agent = ToolAdapterBridge(web_search_tool)

# Use it with the new interface
response = web_search_agent.start("search query")
print(response.output)

# Use it with the legacy interface
result = web_search_agent.generate_query_sequence("search query")
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

## Best Practices

1. Keep agents stateless, with all session data in `AgentState`
2. Use `working_memory` for transient data within a session
3. Design agents to handle a single step at a time
4. Use `tool_registry` for external functionality
5. Return meaningful output in `AgentResponse`