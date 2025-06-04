from communication import GenericRequest, GenericResponse
from tools.abstract_tool import AbstractTool
from tools.registry import register_tool
from typing import List, Dict, Any
from googlesearch import search

class WebSearchTool(AbstractTool):
    def __init__(self):
        self.name = "Web Search"
        self.description = "Search the web for information using Google search."

    def run(self, query: GenericRequest) -> GenericResponse:
        """Run web search using the registered tool function."""
        return search(query.content, advanced=True, num_results=5)

    def get_name(self):
        """Get the tool name."""
        return self.name


