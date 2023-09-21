from models.static_openai_wrapper import StaticOpenAIModel
class BasicAgent:

    def __init__(self):
        # Initialize tools and memory
        self.messages = []
        self.prompt = ""
        self.last_input_message = None
        self.last_response_message = None

    def append_message(self, message, role):
        #if len(self.messages) == 0:
            #self.messages.append({"role": "system", "content": self.prompt})
        if role == "user":
            self.last_input_message = message
        elif role == "assistant":
            self.last_response_message = message
        self.messages.append({"role": role, "content": message})

    def generate_completion(self, text):
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
