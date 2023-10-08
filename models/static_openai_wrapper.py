import config
import openai
import json

class StaticOpenAIModel:

    @staticmethod
    def generate_response(messages):
        config.logger.debug(f"Entering generate_response with messages: {messages}")
        response_obj = openai.ChatCompletion.create(
            #model="gpt-3.5-turbo",
            model="gpt-4",
            messages=messages,
        )

        #return json.dumps(response_obj)
        #response = json.dumps(response)
        config.logger.debug(f"Received response: {response_obj}")
        return response_obj

    @staticmethod
    def generate_embedding(text):
        #config.logger.debug(f"Entering generate_embedding with text: {text}")
        response = openai.Embedding.create(model="text-embedding-ada-002", input=text)
        #config.logger.debug(f"Received response: {response}")
        embedding = response.data[0].embedding
        config.logger.debug(f"Received embedding: {embedding}")
        return embedding
