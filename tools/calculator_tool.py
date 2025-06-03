"""
Calculator tool for performing basic mathematical operations.
"""

import re
from tools.registry import register_tool


@register_tool(
    name="calculator",
    description="Evaluates simple mathematical expressions",
    tags=["math", "utility"],
    version="1.0.0"
)
def calculator_tool(expression: str) -> float:
    """
    Evaluate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "3 * 5")
        
    Returns:
        The result of the calculation
        
    Raises:
        ValueError: If the expression is invalid or unsafe
    """
    # Clean the expression
    expression = expression.strip()
    
    # Simple validation - only allow numbers, operators, parentheses, and whitespace
    if not re.match(r'^[0-9+\-*/().\s]+$', expression):
        raise ValueError(f"Invalid characters in expression: {expression}")
    
    try:
        # Use eval with restricted globals for safety
        result = eval(expression, {"__builtins__": {}})
        return float(result)
    except Exception as e:
        raise ValueError(f"Error evaluating expression '{expression}': {str(e)}")


# Legacy function for backward compatibility
def create_calculator_tool():
    """Create a calculator tool function for legacy usage."""
    return calculator_tool