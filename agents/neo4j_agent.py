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

class Neo4jAgent(AbstractAgent):

    def __init__(self):
        # Initialize tools and memory
        #neo_url = os.environ.get('NEO4J_URI')
        #neo_url = 'bolt://neo4j:7687'
        #self.neo = Neo4jWrapper(uri=neo_url, user='neo4j', password='password')
        self.logger = config.logger
        self.messages = []
        self.prompt = "Your name is Sophia and you are an extremely knowledgable and capable assistant"
        self.cypher_daemon = TextToCypherDaemon()
        self.messages.append({"role": "system", "content": self.prompt})
        self.last_input_message = None
        self.last_response_message = None
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
            # Should go something like this:
            # User input is used to extract relevant info from knowledge graph
            # Extracted info is used to generate a response
            # Response is returned to user
            response = None
            self.append_message(text, "user")

            response = StaticOpenAIModel.generate_response(self.messages)
            response_dict = response.to_dict()
            res = response_dict['choices'][0]['message']['content']
            self.append_message(res, "assistant")
            
            config.logger.debug(f"res: {res}")
            #cypher_query = TextToCypherDaemon.generate_cypher(res)
            #self.neo.query(cypher_query)
            self.memory.record(res)
            #log_message = f"User query: {text}, Cypher query: {cypher_query}, Response: {response}"
            return res

        except Exception as e:
            #self.logger.debug(e)
            return f"Exception returned: {e}"
