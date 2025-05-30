"""
Defines a model response class that encapsulates the response from a model.
"""
from typing import Any, Dict, Optional
class ModelResponse:
    """
    A class to represent a response from a model.

    Attributes:
        data (Dict[str, Any]): The data returned by the model.
        metadata (Optional[Dict[str, Any]]): Optional metadata about the response.
    """

    def __init__(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None, output: Optional[Any] = None):
        self.data = data
        self.output = output
        self.metadata = metadata if metadata is not None else {}

    def __repr__(self) -> str:
        return f"ModelResponse(data={self.data}, metadata={self.metadata})"

