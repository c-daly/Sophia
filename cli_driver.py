#!/usr/bin/env python3
"""
CLI driver for demonstrating the stateful agent framework.

This module provides a simple command-line interface to interact with
agents implemented using the stateful agent framework.
"""

import argparse
import sys
from typing import Dict, Any, Callable
from pathlib import Path

# Add the config directory to sys.path to import the config module
config_dir = Path(__file__).parent / 'config'
sys.path.insert(0, str(config_dir))

from config import get_config
from agents.stateful_conversational_agent import StatefulConversationalAgent
from agents.tool_agent import create_calculator_agent
from agents.agent_loop import AgentLoop
from agents.abstract_agent import AbstractAgent
from agents.sophia_agent import SophiaAgent
import config

def get_available_agents() -> Dict[str, Callable[[], AbstractAgent]]:
    """
    Get a dictionary of available agent factories.
    
    Returns:
        A mapping of agent names to factory functions
    """
    return {
        "conversational": lambda: StatefulConversationalAgent(),
        "calculator": create_calculator_agent,
        "sophia": lambda: SophiaAgent()
    }


def main():
    """Run the CLI driver."""
    # Set up command-line arguments - include both CLI driver and config args
    parser = argparse.ArgumentParser(description="Stateful Agent Framework CLI Driver")
    
    # CLI driver specific arguments
    parser.add_argument(
        "--agent", "-a",
        choices=list(get_available_agents().keys()),
        default="conversational",
        help="The type of agent to use"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )    
    #parser.add_argument(
    #    "--debug", "-d",
    #    action="store_true",
    #    help="Run in debug mode"
    #)
 
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Initial input for the agent"
    )
    
    # Configuration arguments (add config args to the main parser)
    parser.add_argument("--env", type=str, help="Environment (dev/test/prod)")
    parser.add_argument("--config", type=str, help="Path to config override JSON")
    parser.add_argument("--memory", type=str, help="Override memory backend")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--log-level", type=str, help="Override log level")
    parser.add_argument("--mongo-url", type=str, help="Override MongoDB URL")
    parser.add_argument("--neo4j-uri", type=str, help="Override Neo4j URI")
    
    args = parser.parse_args()
    
    # Initialize config with parsed arguments
    config = get_config(args)
    
    # Log the current configuration if debug is enabled
    if config.get("debug"):
        config.logger.debug(f"Running in {config.get_environment()} environment")
        config.logger.debug(f"Configuration: {config.get_all()}")
    
    # Create the selected agent
    agent_factory = get_available_agents()[args.agent]
    agent = agent_factory()
    
    # Create an agent loop
    loop = AgentLoop(agent)
    
    if args.debug:
        config.debug = True
        print("Debug mode enabled. Agent state will be printed after each interaction.")
    if args.interactive:
        # Interactive mode
        if args.input:
            initial_input = args.input
        else:
            print(f"Starting interactive session with {args.agent} agent.")
            print("Enter your message (or 'exit' to quit):")
            initial_input = input("> ")
        
        # Start the interactive loop
        if initial_input.lower() not in ["exit", "quit"]:
            loop.run_interactive(initial_input)
    else:
        # Single response mode
        if not args.input:
            print("Error: Input required in non-interactive mode", file=sys.stderr)
            sys.exit(1)
        
        # Run the agent and print the response
        response = loop.run_until_done(args.input)
        print(response.output)


if __name__ == "__main__":
    main()
