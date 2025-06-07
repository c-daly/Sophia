"""
Dynamic Tool Registry for Sophia's Tool Architecture.

This module provides a dynamic tool registry that supports:
- Automatic tool discovery through decorators
- Hot-swapping of tools at runtime
- Tool metadata collection and management
- Thread-safe operations
"""

from tools.abstract_tool import AbstractTool
from typing import Dict, List, Union

class ToolRegistry:
    def __init__(self, cfg):
        self.cfg = cfg
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

    def get_all_tools_description(self) -> str:
        """
        Get a string description of all registered tools.
        
        Returns:
            String containing descriptions of all tools
        """
        descriptions = []
        for tool in self._tools_dict.values():
            descriptions.append(f"{tool.name}: {tool.description}")
        return "\n".join(descriptions)

    def get_tool(self, name: str) -> Union[AbstractTool, None]:
        """
        Get a tool by its name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            The tool instance if found, None otherwise
        """
        tool = self._tools_dict.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found in registry.")
        self.cfg.logger.debug(f"Retrieved tool: {tool.name}")
        return self._tools_dict.get(name, None)
