from agents.abstract_agent import AbstractAgent
from models.static_openai_wrapper import StaticOpenAIModel
from prompts.prompts import DEFAULT_PROMPT


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
            response = None
            self.text = text
            self.append_message(text, "user")
            response = StaticOpenAIModel.generate_response(self.messages)
            response_text = response.choices[0].message['content'].strip()
            self.append_message(response_text, "assistant")

            return response

        except Exception as e:
            print(e)
            return "There was an error obtaining a response from the model."
