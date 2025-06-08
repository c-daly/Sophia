from communication.generic_request import GenericRequest
from communication.generic_response import GenericResponse
from tools.abstract_tool import AbstractTool
from googlesearch import search

class WebSearchTool(AbstractTool):
    def __init__(self, cfg):
        self.cfg = cfg
        self.name = "WebSearch"
        self.description = "Search the web for information using Google search."

    def run(self, request: GenericRequest) -> GenericResponse:
        """Run web search using the registered tool function."""
        self.cfg.logger.debug(f"Running {self.name} tool with request: {request.content}")
        search_response = search(request.content, advanced=True, num_results=5)

        # convert results to string format
        search_response = "\n".join([f"{i+1}. {result}" for i, result in enumerate(search_response)])
        response = GenericResponse(output=search_response)


        return response

    def get_name(self):
        """Get the tool name."""
        return self.name


