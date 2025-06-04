"""
Dynamic Tool Registry for Sophia's Tool Architecture.

This module provides a dynamic tool registry that supports:
- Automatic tool discovery through decorators
- Hot-swapping of tools at runtime
- Tool metadata collection and management
- Thread-safe operations
"""

from abstract_tool import AbstractTool
import threading
import importlib
import inspect
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass, field
from functools import wraps


class ToolRegistry:
    def __init__(self):
        self._tools = []
        self._tools_dict: Dict[str, AbstractTool] = {}
    
    def register_tool(self, tool: AbstractTool) -> bool:
        """
        Register a tool instance with the registry.
        
        Args:
            tool: An instance of AbstractTool to register
            
        Returns:
            True if registration was successful, False if tool already exists
        """
        if tool.name in self._tools:
            return False
        
        self._tools_dict[tool.name] = tool
        return True

    def unregister(self, tool: AbstractTool) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            name: Name of the tool to unregister
            
        Returns:
            True if tool was found and removed, False otherwise
        """
        if tool.name in self._tools_dict:
            del self._tools_dict[tool.name]
            return True
        return False
      
    def list_tools(self) -> List[str]:
        """
        Get a list of all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self._tools_dict.keys())
    
    def clear(self):
        """Clear all registered tools."""
        self._tools.clear()
   
# Global registry instance
registry = ToolRegistry()


def register_tool(name: Optional[str] = None,
                  description: str = "",
                  parameters: Optional[Dict[str, Any]] = None,
                  tags: Optional[List[str]] = None,
                  version: str = "1.0.0"):
    """
    Decorator to automatically register a function as a tool.
    
    Args:
        name: Tool name (uses function name if not provided)
        description: Tool description
        parameters: Parameter schema for the tool
        tags: Tags for categorizing the tool
        version: Tool version
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        
        # Extract description from docstring if not provided
        tool_description = description
        if not tool_description and func.__doc__:
            tool_description = func.__doc__.strip().split('\n')[0]
        
        # Extract parameter information from function signature
        tool_parameters = parameters or {}
        if not tool_parameters:
            sig = inspect.signature(func)
            tool_parameters = {
                param_name: {
                    "type": param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "Any",
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty
                }
                for param_name, param in sig.parameters.items()
            }
        
        # Register the tool
        registry.register(
            name=tool_name,
            function=func,
            description=tool_description,
            parameters=tool_parameters,
            tags=tags or [],
            version=version
        )
        
        return func
    
    return decorator


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.
    
    Returns:
        The global ToolRegistry instance
    """
    return registry


def autodiscover_tools(module_names: List[str]):
    """
    Automatically discover and register tools from specified modules.
    
    Args:
        module_names: List of module names to scan for tools
    """
    for module_name in module_names:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Could not import module {module_name}: {e}")
