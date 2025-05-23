import openai

"""
     This is a simple static wrapper class for the OpenAI API.
     ChatCompletion and Embedding are offered.
"""
class StaticOpenAIModel:

    @staticmethod
    def generate_response(messages, model="gpt-3.5-turbo"):
       # config.logger.debug(f"Entering generate_response with messages: {messages}")
        response_obj = openai.responses.create(
            model=model,
            input=messages,
        )


        return response_obj

    @staticmethod
    def generate_embedding(text, model="text-embedding-3-small"):
        #config.logger.debug(f"Entering generate_embedding with text: {text}")
        response = openai.Embedding.create(model=model, input=text)
        #config.logger.debug(f"Embedding response: {response.data[0].embedding}")
        embedding = response.data[0].embedding
        return embedding
