# Dynamic Tool Registry

The Dynamic Tool Registry is a core component of Sophia's tool architecture that provides automatic tool discovery, hot-swapping capabilities, and rich metadata management.

## Overview

The Dynamic Tool Registry enables:

- **Automatic Discovery**: Tools are automatically registered when modules are imported
- **Decorator-based Registration**: Simple `@register_tool` decorator for marking functions as tools
- **Hot-swapping**: Runtime replacement of tool implementations
- **Rich Metadata**: Automatic parameter extraction and customizable tool descriptions
- **Thread Safety**: Safe concurrent access to the registry
- **Backward Compatibility**: Works alongside legacy tool implementations

## Quick Start

### Registering a Tool

```python
from tools.registry import register_tool

@register_tool(
    name="my_tool",
    description="A sample tool that does something useful",
    tags=["utility", "sample"],
    version="1.0.0"
)
def my_tool(input_text: str, count: int = 1) -> str:
    """Process input text multiple times."""
    return input_text * count
```

### Using the Registry

```python
from tools.registry import get_registry

registry = get_registry()

# List all available tools
tools = registry.list_tools()
print(f"Available tools: {tools}")

# Get a specific tool
tool_func = registry.get_tool("my_tool")
result = tool_func("Hello ", 3)  # Returns "Hello Hello Hello "

# Get tool metadata
metadata = registry.get_metadata("my_tool")
print(f"Description: {metadata.description}")
print(f"Parameters: {metadata.parameters}")
```

## Core Components

### ToolRegistry Class

The `ToolRegistry` class is the central manager for all tools. It implements a singleton pattern to ensure global consistency.

#### Key Methods

- `register(name, function, description, parameters, tags, version)`: Register a new tool
- `unregister(name)`: Remove a tool from the registry
- `get_tool(name)`: Retrieve a tool function by name
- `get_metadata(name)`: Get metadata for a specific tool
- `list_tools()`: Get all registered tool names
- `hot_swap(name, new_function)`: Replace a tool implementation at runtime
- `get_tools_by_tag(tag)`: Find tools with a specific tag

### ToolMetadata Class

The `ToolMetadata` class stores comprehensive information about each tool:

```python
@dataclass
class ToolMetadata:
    name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    module: str = ""
    function: Optional[Callable] = None
```

### @register_tool Decorator

The decorator automatically registers functions as tools and extracts metadata:

```python
@register_tool(
    name="optional_custom_name",      # Defaults to function name
    description="Tool description",   # Extracted from docstring if not provided
    parameters={"param": "schema"},   # Auto-extracted from function signature
    tags=["tag1", "tag2"],           # Categorization tags
    version="1.0.0"                  # Version string
)
def my_function(param: str) -> str:
    """Function docstring used as description if not provided."""
    return f"Processed: {param}"
```

## Advanced Features

### Hot-Swapping

Replace tool implementations at runtime without restarting the application:

```python
from tools.registry import get_registry

registry = get_registry()

# Original implementation
@register_tool(name="greeter")
def simple_greeter(name: str) -> str:
    return f"Hello, {name}!"

# Later, swap with enhanced version
def enhanced_greeter(name: str) -> str:
    return f"Greetings and salutations, {name}! Welcome!"

registry.hot_swap("greeter", enhanced_greeter)
```

### Automatic Parameter Extraction

The registry automatically extracts parameter information from function signatures:

```python
@register_tool()
def example_tool(
    required_param: str,
    optional_param: int = 42,
    another_param: float = 3.14
) -> str:
    """Example tool with various parameter types."""
    return f"{required_param}: {optional_param}, {another_param}"

# Extracted parameters:
# {
#     "required_param": {"type": "str", "required": true},
#     "optional_param": {"type": "int", "default": 42, "required": false},
#     "another_param": {"type": "float", "default": 3.14, "required": false}
# }
```

### Tool Discovery and Filtering

Find tools by tags or other criteria:

```python
# Get all tools with specific tags
math_tools = registry.get_tools_by_tag("math")
utility_tools = registry.get_tools_by_tag("utility")

# Get complete metadata for all tools
all_metadata = registry.list_tools_with_metadata()

# Filter by version, module, or other criteria
recent_tools = [
    name for name, meta in all_metadata.items()
    if meta["version"].startswith("2.")
]
```

## Integration with AgentLoop

The `AgentLoop` class automatically integrates with the dynamic tool registry:

```python
from agents.agent_loop import AgentLoop
from agents.abstract_agent import AbstractAgent

# AgentLoop automatically uses the global registry
agent_loop = AgentLoop(my_agent)

# Access available tools
available_tools = agent_loop.get_available_tools()
tool_metadata = agent_loop.get_tool_metadata()

# Register legacy tools for backward compatibility
agent_loop.register_legacy_tool("old_tool", old_tool_function)
```

## Best Practices

### Tool Design

1. **Single Responsibility**: Each tool should have one clear purpose
2. **Type Hints**: Use type hints for automatic parameter extraction
3. **Documentation**: Include docstrings for automatic description extraction
4. **Error Handling**: Handle errors gracefully and provide meaningful messages

```python
@register_tool(
    description="Calculate the area of a rectangle",
    tags=["math", "geometry"],
    version="1.0.0"
)
def rectangle_area(width: float, height: float) -> float:
    """
    Calculate the area of a rectangle.
    
    Args:
        width: Width of the rectangle
        height: Height of the rectangle
        
    Returns:
        Area of the rectangle
        
    Raises:
        ValueError: If width or height is negative
    """
    if width < 0 or height < 0:
        raise ValueError("Width and height must be non-negative")
    
    return width * height
```

### Module Organization

1. **Separate Files**: Keep related tools in separate modules
2. **Import Organization**: Use `__init__.py` to control tool discovery
3. **Lazy Loading**: Consider lazy loading for expensive tool imports

```python
# tools/math_tools.py
from tools.registry import register_tool

@register_tool(tags=["math"])
def add(a: float, b: float) -> float:
    return a + b

@register_tool(tags=["math"])
def multiply(a: float, b: float) -> float:
    return a * b

# tools/__init__.py
from . import math_tools  # Triggers registration
```

### Versioning and Updates

1. **Semantic Versioning**: Use semantic versioning for tools
2. **Migration Path**: Provide migration guidance for version updates
3. **Deprecation**: Mark old tools as deprecated before removal

## Thread Safety

The registry is designed to be thread-safe and supports concurrent access:

```python
import threading
from tools.registry import get_registry

def worker_function(worker_id):
    registry = get_registry()
    
    # Safe to register tools from multiple threads
    @register_tool(name=f"worker_tool_{worker_id}")
    def worker_tool():
        return f"Result from worker {worker_id}"
    
    # Safe to access tools from multiple threads
    tool = registry.get_tool("shared_tool")
    if tool:
        result = tool()

# Multiple threads can safely access the registry
threads = [threading.Thread(target=worker_function, args=(i,)) for i in range(5)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

## Migration from Legacy Tools

### Existing Tool Classes

Convert existing `AbstractTool` classes to use the registry:

```python
# Old way
class MyTool(AbstractTool):
    def run(self, args=None):
        return "result"
    
    def get_name(self):
        return "my_tool"

# New way
@register_tool(name="my_tool")
def my_tool_function(args=None):
    """Tool description here."""
    return "result"

# For backward compatibility, keep the class
class MyTool(AbstractTool):
    def run(self, args=None):
        return my_tool_function(args)
    
    def get_name(self):
        return "my_tool"
```

### Legacy AgentLoop Usage

The new `AgentLoop` maintains backward compatibility:

```python
# Old way - still works
legacy_tools = {"tool1": tool1_func, "tool2": tool2_func}
agent_loop = AgentLoop(agent, legacy_tool_registry=legacy_tools)

# New way - automatic discovery
agent_loop = AgentLoop(agent)  # Uses global registry automatically
```

## Error Handling

The registry provides comprehensive error handling:

```python
try:
    tool = registry.get_tool("nonexistent_tool")
    if tool is None:
        print("Tool not found")
        
    result = tool("invalid_input")
except Exception as e:
    print(f"Tool execution failed: {e}")
```

## Debugging and Introspection

Tools for debugging and understanding the registry state:

```python
# List all tools with their metadata
for name in registry.list_tools():
    metadata = registry.get_metadata(name)
    print(f"{name}: {metadata.description}")
    print(f"  Module: {metadata.module}")
    print(f"  Parameters: {list(metadata.parameters.keys())}")
    print(f"  Tags: {metadata.tags}")

# Check if a tool exists
if registry.has_tool("my_tool"):
    print("Tool is registered")

# Get tools by category
text_tools = registry.get_tools_by_tag("text")
print(f"Text processing tools: {text_tools}")
```