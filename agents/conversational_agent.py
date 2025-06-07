# Conversational agent implements an
# agent that can be used to interact with the user.
# The interaction will continue until the agent
# believes the original query has been satisfied


from agents.abstract_agent import AbstractAgent
from models.static_openai_wrapper import StaticOpenAIModel
from prompts.prompt import DefaultPrompt

class ConversationalAgent(AbstractAgent):
    def __init__(self):
        # Initialize tools and memory
        self.messages = []
        self.prompt = ""
        self.continue_message = "Should this conversation continue (yes or no)?"
        self.append_message(self.prompt, "system")
        self.last_input_message = None
        self.last_response_message = None

    def append_message(self, message, role):
        if role == "user":
            self.last_input_message = message
        elif role == "assistant":
            self.last_response_message = message
        self.messages.append({"role": role, "content": message})

    def should_complete(self):
        user_response = input(self.continue_message)
        return user_response == "yes"

    def generate_query_sequence(self, text):
        first_time = True
        while first_time or not self.should_complete():
            try:
                response = None

                self.append_message(text, "user")
                response = StaticOpenAIModel.generate_response(self.messages)
                response_text = response.choices[0].message['content'].strip()
                self.append_message(response_text, "assistant")

                return response

            except Exception as e:
                print(e)
                return "There was an error obtaining a response from the model."
