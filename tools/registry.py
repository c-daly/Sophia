"""
Dynamic Tool Registry for Sophia's Tool Architecture.

This module provides a dynamic tool registry that supports:
- Automatic tool discovery through decorators
- Hot-swapping of tools at runtime
- Tool metadata collection and management
- Thread-safe operations
"""

import threading
import importlib
import inspect
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class ToolMetadata:
    """Metadata information for a registered tool."""
    name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    module: str = ""
    function: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "tags": self.tags,
            "version": self.version,
            "module": self.module
        }


class ToolRegistry:
    """
    Dynamic tool registry supporting automatic discovery and hot-swapping.
    
    This registry maintains a collection of tools that can be dynamically
    registered, unregistered, and discovered at runtime.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ToolRegistry, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the tool registry."""
        if self._initialized:
            return
            
        self._tools: Dict[str, ToolMetadata] = {}
        self._lock = threading.RLock()
        self._initialized = True
    
    def register(self, 
                 name: str, 
                 function: Callable,
                 description: str = "",
                 parameters: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 version: str = "1.0.0") -> bool:
        """
        Register a tool with the registry.
        
        Args:
            name: Unique name for the tool
            function: The callable function that implements the tool
            description: Human-readable description of the tool
            parameters: Parameter schema/description for the tool
            tags: Categories or tags for the tool
            version: Version string for the tool
            
        Returns:
            True if registration was successful, False if tool already exists
        """
        with self._lock:
            if name in self._tools:
                return False
                
            metadata = ToolMetadata(
                name=name,
                description=description,
                parameters=parameters or {},
                tags=tags or [],
                version=version,
                module=function.__module__ if hasattr(function, '__module__') else "",
                function=function
            )
            
            self._tools[name] = metadata
            return True
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            name: Name of the tool to unregister
            
        Returns:
            True if tool was found and removed, False otherwise
        """
        with self._lock:
            if name in self._tools:
                del self._tools[name]
                return True
            return False
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """
        Get a tool function by name.
        
        Args:
            name: Name of the tool
            
        Returns:
            The tool function if found, None otherwise
        """
        with self._lock:
            metadata = self._tools.get(name)
            return metadata.function if metadata else None
    
    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """
        Get metadata for a tool.
        
        Args:
            name: Name of the tool
            
        Returns:
            ToolMetadata object if found, None otherwise
        """
        with self._lock:
            return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """
        Get a list of all registered tool names.
        
        Returns:
            List of tool names
        """
        with self._lock:
            return list(self._tools.keys())
    
    def list_metadata(self) -> List[ToolMetadata]:
        """
        Get metadata for all registered tools.
        
        Returns:
            List of ToolMetadata objects
        """
        with self._lock:
            return list(self._tools.values())
    
    def list_tools_with_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tools with their metadata in dictionary format.
        
        Returns:
            Dictionary mapping tool names to their metadata
        """
        with self._lock:
            return {name: metadata.to_dict() for name, metadata in self._tools.items()}
    
    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            name: Name of the tool
            
        Returns:
            True if tool exists, False otherwise
        """
        with self._lock:
            return name in self._tools
    
    def hot_swap(self, name: str, new_function: Callable) -> bool:
        """
        Hot-swap an existing tool with a new implementation.
        
        Args:
            name: Name of the tool to replace
            new_function: New function implementation
            
        Returns:
            True if swap was successful, False if tool doesn't exist
        """
        with self._lock:
            if name not in self._tools:
                return False
                
            # Update the function while preserving other metadata
            self._tools[name].function = new_function
            self._tools[name].module = new_function.__module__ if hasattr(new_function, '__module__') else ""
            return True
    
    def clear(self):
        """Clear all registered tools."""
        with self._lock:
            self._tools.clear()
    
    def get_tools_by_tag(self, tag: str) -> List[str]:
        """
        Get tools that have a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of tool names that have the specified tag
        """
        with self._lock:
            return [name for name, metadata in self._tools.items() if tag in metadata.tags]


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