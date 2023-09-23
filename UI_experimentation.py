import dash
import time
from dash import dcc, html
from dash.dependencies import Input, Output
from agents.basic_agent import BasicAgent
#from data.pinecone_wrapper import PineconeWrapper
from data.mongo_wrapper import MongoWrapper
from data.milvus_wrapper import MilvusWrapper
from models.static_openai_wrapper import StaticOpenAIModel

# Create a Dash application
app = dash.Dash(__name__)
messages = []
model = BasicAgent()
mongo = MongoWrapper()
# Define the app layout
app.layout = html.Div([
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='Tab One', value='tab-1-example-graph'),
        dcc.Tab(label='Tab Two', value='tab-2-example-graph'),
    ]),
    # Space
    html.Div(style={'height': '20px'}),

    # Request and Response Textareas on the left
    # Text input component and submit button
    html.Div([
        dcc.Input(id='input-box', type='text'),
        html.Button('Submit', id='submit-button')
    ]),
    html.Div([
        html.Div([
            html.Label('Last Outgoing Request:'),
            dcc.Textarea(id='last-request', style={'width': '100%', 'height': '200px'}),

            html.Label('Last Incoming Response:'),
            dcc.Textarea(id='last-response', style={'width': '100%', 'height': '200px'}),
        ], style={'width': '40%', 'float': 'left'}),



        # Space
        html.Div(style={'height': '20px'}),

        # Text area for output display
        html.Div(dcc.Textarea(id='output-area', style={'margin-left': '20px', 'width': '40%', 'height': '600px'}))
    ]),
    # File upload component
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
])

def format_interaction_data(query, response):
    interaction_data = {
                "user_id": "12345",  # An identifier for the user
                "timestamp": time.time(),  # timestamp of the interaction
                "query": query,  # The user's question or command
                "response": response,  # The system's response
                "metadata": {
                    "agent_fitness_rating": ".5", # A rating of how well the response answered the user's query (0-1), estimated by the agent
                    "user_fitness_rating": ".5", # A rating of how well the response answered the user's query (0-1), estimated by the user
                }
            }
    return interaction_data

def save_interaction_to_database(query, response):
    interaction_data = format_interaction_data(query, response)
    mongo_response = mongo.insert_interaction(interaction_data)
    print(f"Mongo response: {mongo_response}")
    print(f"Mongo ID: {mongo_response.inserted_id}")
    return mongo_response.inserted_id

@app.callback(
    [Output('output-area', 'value'),
     Output('input-box', 'value'),
     Output('last-request', 'value'),
     Output('last-response', 'value')],
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')]
)
def update_output(n_clicks, input_value):
    print(f"Entering update_output with n_clicks: {n_clicks} and input_value: {input_value}")
    if n_clicks and input_value:
        response = model.generate_completion(input_value)

        milvus = MilvusWrapper()
        print(f"Response: {response}")
        # Format messages for display
        formatted_messages = '\n'.join([f"[{msg['role'].capitalize()}]: {msg['content']}\n" for msg in model.messages])
        response_text = response.choices[0].message['content']
        id = save_interaction_to_database(input_value, response_text)
        query_embedding = StaticOpenAIModel.generate_embedding(input_value)
        response_embedding = StaticOpenAIModel.generate_embedding(response_text)
        query_id = "q_" + str(id)
        response_id = "r_" + str(id)
        qr = milvus.insert_vector(query_embedding, query_id)
        rr = milvus.insert_vector(response_embedding, response_id)
        result = milvus.search_vectors(query_embedding)
        print(f"Result: {result}")
        print(f"qr: {qr}")
        print(formatted_messages)
        return formatted_messages, '', model.last_input_message, response.choices[0].message['content']
    return '', '','', ''


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
