from agents.abstract_agent import AbstractAgent
from models.static_openai_wrapper import StaticOpenAIModel
from daemons.text_to_cypher_daemon import TextToCypherDaemon
import config
import json
import time
from data.milvus_wrapper import MilvusWrapper
from data.neo4j_wrapper import Neo4jWrapper
from memory.kg_memory import KGMemory
from prompts.prompts import DEFAULT_PROMPT, SUMMARY_PROMPT
import os

NEO4J_URI = os.getenv("NEO4J_URI")
PROMPT = "You are a sophisticated agent with a deep understanding of the world. You can answer questions and provide explanations. You can also ask questions and provide explanations.\nExisting knowledge is stored here: {existing_knowledge}"

class Neo4jAgent(AbstractAgent):

    def __init__(self):
        # Initialize tools and memory
        self.logger = config.logger
        self.messages = []
        self.messages.append({"role": "system", "content": PROMPT})
        self.memory = KGMemory()
   
    def append_message(self, message, role):
        if role == "user":
            self.last_input_message = message
        elif role == "assistant":
            self.last_response_message = message
        self.messages.append({"role": role, "content": message})

    """ 
        Generate a response to a user query.
        :param text: The user query.
        :return: The response to the user query.
    """
    def generate_query_sequence(self, text):
        try:
            self.append_message(text, "user")
            response = StaticOpenAIModel.generate_response(self.messages)
            response_dict = response.to_dict()
            res = response['choices'][0]['message']['content']
            self.append_message(res, "assistant")
            config.logger.debug(f"res: {res}")
            self.memory.record(res)
            return res

        except Exception as e:
            return f"Exception returned: {e}"
