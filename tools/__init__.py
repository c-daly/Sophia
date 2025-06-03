"""
Tools package for Sophia.

This package provides a dynamic tool registry and collection of tools
for use with Sophia's agent framework.
"""

from .registry import get_registry, register_tool, autodiscover_tools
from .abstract_tool import AbstractTool

# Import tool modules to trigger registration
from . import calculator_tool
from . import web_search_tool

# Export main components
__all__ = [
    'get_registry',
    'register_tool', 
    'autodiscover_tools',
    'AbstractTool'
]


def get_available_tools():
    """Get a list of all available tools."""
    return get_registry().list_tools()


def get_tool_metadata():
    """Get metadata for all available tools."""
    return get_registry().list_tools_with_metadata()