import os
import openai
import json

class StaticOpenAIModel:

    @staticmethod
    def generate_response(messages):
        response_obj = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        #response = response_obj.choices[0].message['content'].strip()
        json.dumps(response_obj)
        return response_obj

    @staticmethod
    def generate_embedding(text):
        response = openai.Embedding.create(model="text-embedding-ada-002", input=text)
        embedding = response.data[0].embedding
        return embedding