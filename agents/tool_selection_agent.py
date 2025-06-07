from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState
from communication.generic_response import GenericResponse
from communication.generic_request import GenericRequest
from models.openai_wrapper import OpenAIModel
from prompts.prompts import TOOL_SELECTION_PROMPT
from tools.registry import ToolRegistry


class ToolSelectionAgent(AbstractAgent):
    """
    A conversational agent implemented using the stateful agent framework.
    
    This agent processes messages one step at a time, maintaining conversation history
    and state between interactions.
    """
    
    def __init__(self, config, tool_registry: ToolRegistry): 
        """
        Initialize the agent.
        
        Args:
            system_prompt: The system prompt to use for the agent
        """
        super().__init__(config)
        self.tool_registry = tool_registry
        tool_descriptions = self.tool_registry.get_all_tools_description()

        self.prompt = TOOL_SELECTION_PROMPT.format(tools=tool_descriptions)

        self.model = OpenAIModel(temperature=0.0)
                

    def start(self, input_content: str, **metadata) -> GenericResponse:
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
        state.add_message("system", self.prompt)
        state.add_message("user", input_content)
        
        # Set the input for processing
        state.user_msg = GenericRequest(content=input_content, metadata=metadata)
        state.input = GenericRequest(content=input_content, metadata=metadata)
        # Process this initial state
        return self.step(state)
    
    def step(self, state: AgentState) -> GenericResponse:
        """
        Process a single step in the conversation.
        
        Args:
            state: The current conversation state
            
        Returns:
            An AgentResponse with the updated state and agent's output
        """
        try:
            # This selection should ultimately be dynamic
            response = self.model.generate_response(state.get_messages_for_llm())

            response_text = response.output


            # Update the state with the new assistant response
            state.add_message("assistant", response_text)
            
            # Set the next action to respond with the generated text
            #state.next_action = AgentAction.respond(
            #    content=response_text,
            #    metadata={"thinking_style": thinking_config.style.name}
            #)
            
            return GenericResponse(
                state=state,
                output=response_text,
                is_done=False  # Conversation can continue
            )
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            state.add_message("system", error_message)
            
            return GenericResponse(
                state=state,
                output=error_message,
                is_done=True  # End conversation due to error
            )
   
