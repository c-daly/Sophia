from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, AgentAction, ActionType
from models.static_openai_wrapper import StaticOpenAIModel
from prompts.prompts import DEFAULT_PROMPT
import agents.thinking_styles as thinking_styles


class SophiaAgent(AbstractAgent):
    """
    A conversational agent implemented using the stateful agent framework.
    
    This agent processes messages one step at a time, maintaining conversation history
    and state between interactions.
    """
    
    def __init__(self, system_prompt=DEFAULT_PROMPT):
        """
        Initialize the agent.
        
        Args:
            system_prompt: The system prompt to use for the agent
        """
        self.system_prompt = system_prompt

    
    def start(self, input_content: str, **metadata) -> AgentResponse:
        """
        Start a new session.
        
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
        state.user_msg = AgentInput(content=input_content, metadata=metadata)
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
            thinking_config = thinking_styles.ThinkingConfig(style=thinking_styles.ThinkStyle.REFLEX, max_iterations=3)
            response = thinking_styles.think(StaticOpenAIModel.generate_response, state, thinking_config)
            # Generate a response using the current history
            #response = StaticOpenAIModel.generate_response(state.get_messages_for_llm())
            response_text = response.output_text
            
            # Update the state with the new assistant response
            state.add_message("assistant", response_text)
            
            # Set the next action to respond with the generated text
            state.next_action = AgentAction(
                type=ActionType.RESPOND,
                content=response_text
            )
            
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
   
