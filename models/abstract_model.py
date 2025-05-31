"""
Provides a unified interface for interacting with different LLM models.
"""

from abc import ABC, abstractmethod
from models.model_response import ModelResponse
from typing import Any
class AbstractModel(ABC):
    """
    Abstract base class for LLM model interfaces.
    """

    @abstractmethod
    def generate_response(self, messages, model) -> ModelResponse:
        """
        Generate text based on the provided prompt.

        :param prompt: The input text to generate a response for.
        :param kwargs: Additional parameters for text generation.
        :return: Generated text as a string.
        """
        pass

