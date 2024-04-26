# tab1_callbacks.py
import config
from dash import Input, Output, State, dcc
from app import app  # Import the app instance from app.py

import time
import markdown

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
        response = app.model.generate_query_sequence(input_value)
        # Format messages for display
        formatted_messages = '\n'.join([f"[{msg['role'].capitalize()}]: {msg['content']}\n" for msg in app.model.messages])

        return formatted_messages, '', input_value, response
    return '', '','', ''

