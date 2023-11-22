from agents.abstract_agent import AbstractAgent
from models.static_openai_wrapper import StaticOpenAIModel
import config
import json
import time
from data.milvus_wrapper import MilvusWrapper
from prompts.prompts import DEFAULT_PROMPT, SUMMARY_PROMPT

class CommandAgent(AbstractAgent):

    def __init__(self):
        # Initialize tools and memory
        self.milvus = None
        self.summaries = []
        self.state = "IDLE"
        self.logger = config.logger
        self.messages = []
        self.prompt = DEFAULT_PROMPT

        self.messages.append({"role": "system", "content": self.prompt})
        self.last_input_message = None
        self.last_response_message = None

    def format_interaction_data(self):
        interaction_data = {
            "user_id": "12345",  # An identifier for the user
            "timestamp": time.time(),  # timestamp of the start of interaction
            "messages": self.messages[1:],  # A list of messages in the interaction excluding the prompt
            "metadata": {
                "agent_fitness_rating": ".5",
                # A rating of how well the response answered the user's query (0-1), estimated by the agent
                "user_fitness_rating": ".5",
                # A rating of how well the response answered the user's query (0-1), estimated by the user
            }
        }
        return interaction_data

    def save_interaction_to_database(self):
        if not self.milvus:
            if not config.milvus:
                config.milvus = MilvusWrapper()
            self.milvus = config.milvus
        summary_messages = list(self.messages)
        summary_messages.append({"role": "system", "content": SUMMARY_PROMPT})
        response = StaticOpenAIModel.generate_response(summary_messages)

        response_dict = response.to_dict()
        summary = response_dict['choices'][0]['message']['content']
        interaction_data = self.format_interaction_data()
        mongo_response = config.mongo.insert_interaction(interaction_data)
        id = mongo_response.inserted_id
        summary_embedding = StaticOpenAIModel.generate_embedding(summary)
        self.milvus.insert_vector(summary_embedding, str(id))
        #self.messages.append({"role": "assistant", "content": summary})
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})
        return mongo_response.inserted_id

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
            response = None
            self.append_message(text, "user")
            response = StaticOpenAIModel.generate_response(self.messages)
            response_dict = response.to_dict()
            res = response_dict['choices'][0]['message']['content']
            try:
                res_dict = json.loads(res, strict=False)
                #self.logger.debug(f"res_dict: {res_dict}, type: {type(res_dict)}")

            except Exception as e:
                self.append_message(f"The following exception occurred while parsing your response: {e}. Please attempt to reformat and send again.", "user")
                response = StaticOpenAIModel.generate_response(self.messages)
                response_dict = response.to_dict()
                #config.logger.debug(f"exception response_dict: {response_dict}, type: {type(response_dict)}")

                res = response_dict['choices'][0]['message']['content']
                #config.logger.debug(f"debug res: {res}, type: {type(res)}")
                res_dict = json.loads(res, strict=False)
                #self.logger.debug(f"exception res_dict: {res_dict}, type: {type(res_dict)}")
            self.append_message(res, "assistant")
            if self.state == "CONFIRMATION_REQUESTED" and text == "yes":
                self.save_interaction_to_database()
                self.state = "IDLE"
            elif res_dict['response_type'] == "confirmation" and self.state != "CONFIRMATION_REQUESTED":
                self.state = "CONFIRMATION_REQUESTED"

            return res_dict['response']

        except Exception as e:
            #self.logger.debug(e)
            return f"Exception returned: {e}"
