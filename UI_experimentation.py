import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from agents.basic_agent import BasicAgent

# Create a Dash application
app = dash.Dash(__name__)
messages = []
model = BasicAgent()
# Define the app layout
app.layout = html.Div([

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


@app.callback(
    [Output('output-area', 'value'),
     Output('input-box', 'value'),
     Output('last-request', 'value'),
     Output('last-response', 'value')],
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')]
)
def update_output(n_clicks, input_value):
    if n_clicks and input_value:
        #messages.append(input_message)
        response = model.generate_completion(input_value)


        print(f"Response: {response}")
        # Format messages for display
        formatted_messages = '\n'.join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in model.messages])
        return response.choices[0].message['content'], '',input_value, str(response)
    #return '1', '2'


# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
