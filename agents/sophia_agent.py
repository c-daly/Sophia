from agents.abstract_agent import AbstractAgent
from agents.agent_interfaces import AgentState, AgentInput, AgentResponse, AgentAction, ActionType
from communication.generic_response import GenericResponse
from communication.generic_request import GenericRequest
from models.openai_wrapper import OpenAIModel
from prompts.prompts import DEFAULT_PROMPT
import agents.thinking_styles as thinking_styles
import config
from agents.tool_selection_agent import ToolSelectionAgent
from tools.registry import ToolRegistry
from tools.web_search_tool import WebSearchTool
import json

class SophiaAgent(AbstractAgent):
    """
    A conversational agent implemented using the stateful agent framework.
    
    This agent processes messages one step at a time, maintaining conversation history
    and state between interactions.
    """
    
    def __init__(self, cfg, system_prompt=DEFAULT_PROMPT):
        """
        Initialize the agent.
        
        Args:
            system_prompt: The system prompt to use for the agent
        """
        super().__init__(cfg)
        web_search_tool = WebSearchTool(cfg)
        self.tool_registry = ToolRegistry(cfg)
        self.tool_registry.register_tool(web_search_tool)
        self.tool_selector = ToolSelectionAgent(cfg, self.tool_registry)
        self.prompt = system_prompt
        self.model = OpenAIModel()
                

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
        #self.logger.debug(f"Processing step with state: {state}")
        try:
            # Consider if tool selection is needed
           
            tool_response = self.tool_selector.start(state.input.content)
            tool_json = json.loads(tool_response.output)
            self.logger.debug(f"Tool result: {tool_json['tool']}")
            tool = self.tool_registry.get_tool(tool_json['tool'])
            tool_request = GenericRequest(content=tool_json['input'])
            tool_result = tool.run(tool_request)
            self.logger.debug(f"search result: {[result for result in tool_result.output]}")
            # This selection should ultimately be dynamic
            thinking_config = thinking_styles.ThinkingConfig(style=thinking_styles.ThinkStyle.REFLEX, max_iterations=3, cot=thinking_styles.CoTVisibility.EXPOSE)
            response = thinking_styles.think(self.model, state, thinking_config, self.logger)


            response_text = response.output
            
            # Update the state with the new assistant response
            state.add_message("assistant", response_text)
            
            # Set the next action to respond with the generated text
            #state.next_action = AgentAction.respond(
            #    content=response_text,
            #    metadata={"thinking_style": thinking_config.style.name}
            #)
            # Log the response 
            #self.logger.info(f"Generated response: {response_text}")
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
   
