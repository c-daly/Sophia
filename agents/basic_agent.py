from agents.abstract_agent import AbstractAgent
import config
from models.static_openai_wrapper import StaticOpenAIModel
from prompts.prompts import DEFAULT_PROMPT
from agents.agent_interfaces import AgentState, AgentResponse


class BasicAgent(AbstractAgent):

    def __init__(self, prompt=DEFAULT_PROMPT):
        # Initialize tools and memory
        self.messages = []
        self.prompt = prompt
        self.append_message(self.prompt, "system")

    def format_query_response_pair(self, response):
        human_score = 0.5
        return {"input_message": self.text, "output_message": response, "human_score": human_score}

    def append_message(self, message, role):
        self.messages.append({"role": role, "content": message})

    def generate_query_sequence(self, text):
        try:
            self.text = text
            self.append_message(text, "user")
            #config.logger.info(f"Sending messages: {self.messages}")
            response = StaticOpenAIModel.generate_response(self.messages)
            response_text = response.choices[0].message['content'].strip()
            self.append_message(response_text, "assistant")

            return response

        except Exception as e:
            print(e)
            return "There was an error obtaining a response from the model."
            
    def start(self, input_content: str, **metadata) -> AgentResponse:
        """
        Implementation of stateful agent interface.
        Start a new conversation with the agent.
        
        Args:
            input_content: The initial user message
            metadata: Additional context
            
        Returns:
            The agent's response
        """
        state = AgentState()
        state.add_message("system", self.prompt)
        state.add_message("user", input_content)
        
        return self.step(state)
    
    def step(self, state: AgentState) -> AgentResponse:
        """
        Process the next step in the conversation.
        
        Args:
            state: The current conversation state
            
        Returns:
            The agent's response
        """
        try:
            # Convert state messages to format expected by OpenAI
            messages = state.get_messages_for_llm()
            
            # Generate response
            response = StaticOpenAIModel.generate_response(messages)
            response_text = response.choices[0].message['content'].strip()
            
            # Update state
            state.add_message("assistant", response_text)
            
            return AgentResponse(
                state=state,
                output=response_text,
                is_done=True
            )
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            state.add_message("system", error_msg)
            
            return AgentResponse(
                state=state,
                output=error_msg,
                is_done=True
            )
