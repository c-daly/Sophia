"""
Stateful conversational agent implementation.

This module implements a conversational agent using the stateful agent framework.
It serves as an example of how to build agents with the new lifecycle model.
"""

from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, AgentAction, ActionType
from models.openai_wrapper import OpenAIModel as OpenAIModel
from prompts.prompts import DEFAULT_PROMPT


class StatefulConversationalAgent(AbstractAgent):
    """
    A conversational agent implemented using the stateful agent framework.
    
    This agent processes messages one step at a time, maintaining conversation history
    and state between interactions.
    """
    
    def __init__(self, model=None, system_prompt=DEFAULT_PROMPT):
        """
        Initialize the stateful conversational agent.
        
        Args:
            system_prompt: The system prompt to use for the agent
        """
        self.system_prompt = system_prompt
        self.model = model if model else OpenAIModel()
    
    def start(self, input_content: str, **metadata) -> AgentResponse:
        """
        Start a new conversation session.
        
        Args:
            input_content: The initial user input
            metadata: Additional metadata for the session
            
        Returns:
            An AgentResponse with the initialized state
        """
        # Create a new state for this session
        state = AgentState()
        
        # Add the system prompt and initial user message
        state.add_message("system", self.system_prompt)
        state.add_message("user", input_content)
        
        # Set the input for processing
        state.input = AgentInput(content=input_content, metadata=metadata)
        
        # Process this initial state
        return self.step(state)
    
    def step(self, state: AgentState) -> AgentResponse:
        """
        Process a single step in the conversation.
        
        Args:
            state: The current conversation state
            
        Returns:
            An AgentResponse with the updated state and agent's output
        """
        try:
            # Generate a response using the current history
            response = self.model.generate_response(state.get_messages_for_llm())
            response_text = response.output
            
            # Update the state with the new assistant response
            state.add_message("assistant", response_text)
            
            # Set the next action to respond with the generated text
            state.next_action = AgentAction.respond(response_text)
            
            return AgentResponse(
                state=state,
                output=response_text,
                is_done=False  # Conversation can continue
            )
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            state.add_message("system", error_message)
            
            return AgentResponse(
                state=state,
                output=error_message,
                is_done=True  # End conversation due to error
            )
    
    def generate_query_sequence(self, text):
        """
        Legacy method implementation for backward compatibility.
        
        Args:
            text: The user input text
            
        Returns:
            The response text
        """
        # Use the new stateful methods but wrap as the old interface expects
        response = self.start(text)
        return response.output
