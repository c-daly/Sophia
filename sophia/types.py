"""
Core data types for Sophia's agent architecture.

These types facilitate communication between different components of Sophia
and provide a consistent interface for agent inputs and outputs.
"""

from typing import Dict, Any, Optional


class AgentInput:
    """
    Represents input to a Sophia agent.

    Currently supports only text input, but designed to be extensible
    for future multimodal capabilities (like speech and visual input).

    The metadata field allows for additional contextual information to be
    passed to the agent without modifying the core class structure.

    Examples:
        >>> from sophia.types import AgentInput
        >>> # Basic usage with just text
        >>> input1 = AgentInput(text="Tell me about the weather")
        >>> # Usage with metadata
        >>> input2 = AgentInput(
        ...     text="How are you feeling?",
        ...     metadata={"source": "web_ui", "timestamp": "2023-05-22T10:15:30Z"}
        ... )
    """

    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an agent input with text and optional metadata.

        Args:
            text: The text input to the agent
            metadata: Optional dictionary containing additional information
        """
        self.text = text
        self.metadata = metadata or {}


class AgentOutput:
    """
    Represents output from a Sophia agent.

    Currently supports only text output, but designed to be extensible
    for future multimodal capabilities (like speech and visual output).

    The metadata field allows for additional information about the response
    to be included, such as confidence scores, emotion, tools used, etc.,
    without modifying the core class structure.

    Examples:
        >>> from sophia.types import AgentOutput
        >>> # Basic usage with just text
        >>> output1 = AgentOutput(text="It's currently sunny and 72 degrees.")
        >>> # Usage with metadata about tools and processing
        >>> output2 = AgentOutput(
        ...     text="I'm feeling contemplative today.",
        ...     metadata={
        ...         "emotion": "thoughtful",
        ...         "tools_used": ["EmotionAnalyzer"],
        ...         "processing_time_ms": 150
        ...     }
        ... )
    """

    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an agent output with text and optional metadata.

        Args:
            text: The text response from the agent
            metadata: Optional dictionary containing additional information
        """
        self.text = text
        self.metadata = metadata or {}