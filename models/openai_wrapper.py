import openai
import config
from models.abstract_model import AbstractModel
from models.model_response import ModelResponse

"""
     This is a simple static wrapper class for the OpenAI API.
     ChatCompletion and Embedding are offered.
"""
class OpenAIModel(AbstractModel):

    def generate_response(self, messages, model="gpt-3.5-turbo"):
        if config.debug:
            config.logger.debug(f"Debug mode is enabled. Messages: {messages}")
        response_obj = openai.responses.create(
            model=model,
            input=messages,
        )

        response = ModelResponse(
                    data = response_obj,
                    output = response_obj.output_text,
                )

        return response

    def generate_embedding(self, text, model="text-embedding-3-small"):
        response = openai.Embedding.create(model=model, input=text)
        embedding = response.data[0].embedding
        return embedding
