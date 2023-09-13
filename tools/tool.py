from abc import ABC, abstractmethod
import httpx

# Define the abstract base class for all tools
class Tool(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def invoke(self, query):
        """Invoke the tool with a specific query and get the result."""
        pass

# Define the SearchTool derived from the Tool ABC
class SearchTool(Tool):
    def __init__(self, model, prompt="Search the web for: {query}"):
        super().__init__(model)
        self.prompt = prompt

    def invoke(self, query):
        # Mocking the search functionality here; in a real environment, this would involve actual web search logic
        # The prompt can be used to provide more context to the LLM or any other search mechanism
        return f"Web search results for '{query}' would be displayed here."

class WikipediaTool:
    def invoke(query):
        return httpx.get("https://en.wikipedia.org/w/api.php", params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }).json()["query"]["search"][0]["snippet"]

class CalculatorTool:
    def invoke(query):
        return eval(query)
# Example usage
#search_tool = SearchTool(None)  # Passing None for the model since it's not used in this mock example
#search_result = search_tool.invoke("current weather in New York")

#search_result
