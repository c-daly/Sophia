from agents.abstract_agent import AbstractAgent
from models.static_openai_wrapper import StaticOpenAIModel
import config
import re
import json
import time

class CommandAgent(AbstractAgent):

    def __init__(self):
        # Initialize tools and memory
        self.summaries = []
        self.state = "IDLE"
        self.logger = config.logger
        self.messages = []
        self.prompt = """
                        Instruction to Agent:
                        Your name is Sophia and you are a highly intelligent assistant capable of understanding the 
                        intent of your user. When receiving new input, you will analyze it to determine if clarification 
                        is required, such as the query contains too much ambiguity, is missing information, or is simply 
                        too broad a question.
                        
                        Record your analysis in one or two words in the assessment variable. Try to understand the
                        intent of the user, and also their level of understanding of the topic.

                        If you believe you need clarification or if a topic is simply too broad to answer succinctly, 
                        record your response_type as clarification. Please don't be in too much of a hurry to ask for 
                        clarification. If a credible snapshot of the information can be given, do so, and give the user 
                        the opportunity to ask follow-up questions when you confirm the response.

                        If you are prepared to reply to the query, record your response_type as confirmation. The 
                        response field will contain your response to the user, plus a request for confirmation that the 
                        user agrees this line of inquiry can be ended. You must use a phrase that forces a yes or no 
                        response.
                       
                        If you are unable to answer the query, record your response_type as unable, with the response
                        as the reason.
                         
                        In all cases the response you send to the user should be recorded in the response variable.
                       
                        Examples:
                            If a user asks about the weather forecast but does not specify a location, prompt for the 
                            location before proceeding to provide the forecast.
                            If a user inquires about a complex or nuanced topic, summarize your understanding of their 
                            inquiry, and ask for confirmation or additional details as necessary.


                        Please format your response as a json object.  Only the response field will be visible to the
                        user. 
                        Please limit markdown content to the response field only.
                        Please format that field with markdown to make the response more readable.
                        Please make sure that the response field can be read by the python eval function.
                         
                        use LaTeX to write mathematical equations in Markdown
                        
                        For example:
                            For a single-line equation, use a single dollar sign before and after the equation, like 
                            this: $E=mc^2$.
                            
                            For a multi-line equation, use two dollar signs before and after the equation, like 
                            this: $$E=mc^2$$
                           
                        Please be mindful that any markup you produce will be embedded in a json document,
                        REMINDER: Only the response field should be formatted with markdown.
                        The response must be compliant with the JSON standard.
                        
                        You must always seek confirmation from the user that their inquiry has been addressed 
                        satisfactorily, except in the case you are unable to answer the query or you are asking for 
                        clarification. You must always ask for confirmation in a way that forces a yes or no response, 
                        with yes indicating the line of inquiry can be closed.
                        
                        After the user confirms the response, you will respond with a pleasantry that invites the
                        user to ask another question. record the response_type for this message as confirmation.
                        
                        Please validate that all quotes are properly escaped before returning. The content portion of 
                        your response will be used as an argument to python's eval function, so it's important that the 
                        response is properly formatted.
                    """

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
        summary_messages = list(self.messages)
        summary_messages.append({"role": "system", "content": "Please summarize the preceding conversation. Please don't neglect to include the factual content when summarizing. Please omit any mention of the user's confirmation at the end. It's sufficient to summarize the conversation up to the point of the user's confirmation."})
        summary = StaticOpenAIModel.generate_response(summary_messages)

        # This can't stay here but just doing it this way for refactor
        interaction_data = self.format_interaction_data()
        mongo_response = config.mongo.insert_interaction(interaction_data)
        print(f"Mongo response: {mongo_response}")
        print(f"Mongo ID: {mongo_response.inserted_id}")
        self.logger.debug(f"Summary: {summary}")
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})
        self.messages.append({"role": "system", "content": summary.choices[0].message['content']})
        self.summaries.append(summary.choices[0].message['content'])
        return mongo_response.inserted_id

    def append_message(self, message, role):
        # if len(self.messages) == 0:
        # self.messages.append({"role": "system", "content": self.prompt})
        if role == "user":
            self.last_input_message = message
        elif role == "assistant":
            self.last_response_message = message
        self.messages.append({"role": role, "content": message})

    def generate_query_sequence(self, text):
        #self.logger.debug(f"Entering generate_query_sequence with text: {text}")
        try:
            response = None

            self.append_message(text, "user")
            response = StaticOpenAIModel.generate_response(self.messages)
            response_dict = response.to_dict()
            #self.logger.debug(f"response_dict: {response_dict}, type: {type(response_dict)}")
            #self.logger.debug(f"response_dict['choices']['message']: {response_dict['choices'][0]['message']}, type: {type(response_dict['choices'][0]['message'])}")
            #self.logger.debug(f"response_dict['choices']['message']['content']: {response_dict['choices'][0]['message']['content']}, type: {type(response_dict['choices'][0]['message']['content'])}")
            res = response_dict['choices'][0]['message']['content']
            self.logger.debug(f"res: {res}, type: {type(res)}")
            try:
                res_dict = json.loads(res, strict=False)
            except Exception as e:
                self.append_message(f"The following exception occurred while parsing your response: {e}. Please attempt to reformat and send again.", "user")
                response = StaticOpenAIModel.generate_response(self.messages)
                response_dict = response.to_dict()
                res = response_dict['choices'][0]['message']['content']
                config.logger.debug(f"debug res: {res}, type: {type(res)}")
                res_dict = json.loads(res, strict=False)
            self.logger.debug(f"res_dict: {res_dict}, type: {type(res_dict)}")
            self.logger.debug(f"response: {res_dict['response']}")
            self.logger.debug(f"last message response_type: {self.messages[-1]['response_type']}")
            self.logger.debug(f"text: {text}")

            self.append_message(res, "assistant")

            if res_dict['response_type'] == "confirmation" and text == 'yes':
                self.save_interaction_to_database()

            return res_dict['response']

        except Exception as e:
            self.logger.debug(e)
            return f"Exception returned: {e}"
