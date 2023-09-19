from models.static_openai_wrapper import StaticOpenAIModel
class BasicAgent:

    def __init__(self):
        # Initialize tools and memory
        self.messages = []
        self.prompt = ""

    def append_message(self, message, role):
        #if len(self.messages) == 0:
            #self.messages.append({"role": "system", "content": self.prompt})
        self.messages.append({"role": role, "content": message})

    def generate_completion(self, text):
        try:
            response = None

            self.append_message(text, "user")
            response = StaticOpenAIModel.generate_response(self.messages)
            self.append_message(response, "assistant")

            print(response)
            return response

        except Exception as e:
            print(e)
            return "There was an error obtaining a response from the model."
