import os
import openai

class OpenAIModel:
    def __init__(self, prompt_template="{input_text}"):
        self.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_key = self.api_key
        self.prompt_template = prompt_template

    def generate_response(self, messages=None):
        # Construct the message input
        #if messages is None:
        #    messages = {"role": "user", "content": user_input}

        #if past_interactions:
        #    messages.extend(past_interactions)

        response_obj = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        #response = response_obj.choices[0].message['content'].strip()
        response = response_obj.choices[0].message
        return response

    def generate_embedding(self, text):
        response = openai.Embedding.create(model="text-embedding-ada-002", input=text)
        embedding = response.data[0].embedding
        #return embedding
        return embedding