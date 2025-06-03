import os
import openai
import sys
from pathlib import Path

# Add the config directory to sys.path to import the config module
config_dir = Path(__file__).parent.parent / 'config'
sys.path.insert(0, str(config_dir))
from config import get_config

class OpenAIModel:
    def __init__(self, prompt_template="{input_text}"):
        # Use centralized config for OpenAI API key
        self._config = get_config()
        self.api_key = self._config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in config or environment variables")
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