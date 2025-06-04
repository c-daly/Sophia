from communication import GenericRequest, GenericResponse
from tools.abstract_tool import AbstractTool
from tools.registry import register_tool
from typing import List, Dict, Any
from googlesearch import search

class WebSearchTool(AbstractTool):
    def __init__(self):
        self.name = "Web Search"
        self.description = "Search the web for information using Google search."

    def run(self, request: GenericRequest) -> GenericResponse:
        """Run web search using the registered tool function."""
        response = GenericResponse(output=search(request.content, num_results=5))
        return response

    def get_name(self):
        """Get the tool name."""
        return self.name


