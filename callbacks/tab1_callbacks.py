# tab1_callbacks.py
import config
from dash import Input, Output, State, dcc
from app import app  # Import the app instance from app.py
from models.static_openai_wrapper import StaticOpenAIModel
from data.mongo_wrapper import MongoWrapper
from data.milvus_wrapper import MilvusWrapper
import time
import json
import markdown

def format_interaction_data(query, response):
    interaction_data = {
                "user_id": "12345",  # An identifier for the user
                "timestamp": time.time(),  # timestamp of the start of interaction
                "messages": app.model.messages,  # A list of messages in the interaction
                "metadata": {
                    "agent_fitness_rating": ".5", # A rating of how well the response answered the user's query (0-1), estimated by the agent
                    "user_fitness_rating": ".5", # A rating of how well the response answered the user's query (0-1), estimated by the user
                }
            }
    return interaction_data

def save_interaction_to_database(query, response):
    # This can't stay here but just doing it this way for refactor
    mongo = MongoWrapper()
    interaction_data = format_interaction_data(query, response)
    mongo_response = mongo.insert_interaction(interaction_data)
    print(f"Mongo response: {mongo_response}")
    print(f"Mongo ID: {mongo_response.inserted_id}")
    return mongo_response.inserted_id

@app.callback(
    [Output('output-area', 'value'),
     Output('input-box', 'value'),
     Output('last-request', 'value'),
     Output('last-response', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('input-box', 'value')]
)
def update_output(n_clicks, input_value):
    print(f"Entering update_output with n_clicks: {n_clicks} and input_value: {input_value}")
    if n_clicks and input_value:
        #milvus = MilvusWrapper()
        response = app.model.generate_query_sequence(input_value)
        config.logger.debug("generate returned")
        #response = json.loads(json.dumps(response))
        response_content = markdown.markdown(response)
        config.logger.debug(f"response_content: {response_content}, type: {type(response_content)}")
        #response_obj = json.loads(json.dumps(response_content))
        #config.logger.debug(f"response_obj: {response_obj}, type: {type(response_obj)}")
        # Format messages for display
        formatted_messages = '\n'.join([f"[{msg['role'].capitalize()}]: {msg['content']}\n" for msg in app.model.messages[1:]])
        #id = save_interaction_to_database(input_value, response_text)
        #query_embedding = StaticOpenAIModel.generate_embedding(input_value)
        #response_embedding = StaticOpenAIModel.generate_embedding(response_text)
        #query_id = "q_" + str(id)
        #response_id = "r_" + str(id)
        #qr = milvus.insert_vector(query_embedding, query_id)
        #rr = milvus.insert_vector(response_embedding, response_id)
        #result = milvus.search_vectors(query_embedding)
        #print(f"Result: {result}")
        #print(f"qr: {qr}")
        #response = json.loads(response.choices[0].message['content'])
        #response_content = response['response']
        return formatted_messages, '', app.model.last_input_message, response
    return '', '','', ''

