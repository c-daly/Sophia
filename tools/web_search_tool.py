from tools.abstract_tool import AbstractTool
from tools.registry import register_tool
from typing import List, Dict, Any

try:
    from googlesearch import search
    GOOGLESEARCH_AVAILABLE = True
except ImportError:
    GOOGLESEARCH_AVAILABLE = False


@register_tool(
    name="web_search",
    description="Search the web for information using Google search",
    tags=["search", "web", "information"],
    version="1.0.0"
)
def web_search_tool(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web for information using Google search.
    
    Args:
        query: Search query string
        num_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of search results with title, url, and description
    """
    if not GOOGLESEARCH_AVAILABLE:
        raise RuntimeError("googlesearch-python package not available")
        
    try:
        results = search(query, advanced=True, num_results=num_results)
        return results
    except Exception as e:
        raise RuntimeError(f"Web search failed: {str(e)}")


class WebSearchTool(AbstractTool):
    """Legacy WebSearchTool class for backward compatibility."""
    
    def __init__(self):
        self.name = "Web Search"

    def run(self, query):
        """Run web search using the registered tool function."""
        return web_search_tool(query)

    def get_name(self):
        """Get the tool name."""
        return self.name


