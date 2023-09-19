# Import required libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from openai_model import OpenAIModel
from agents.ToolBasedAgentWithFeedback import ToolBasedAgentWithFeedback
# Create a Dash application
app = dash.Dash(__name__)
messages = []
model = ToolBasedAgentWithFeedback()
# Define the app layout
app.layout = html.Div([
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
    # Space
    html.Div(style={'height': '20px'}),

    # Text input component and submit button
    html.Div([
        dcc.Input(id='input-box', type='text', style={'marginRight': '10px'}),
        html.Button('Submit', id='submit-button')
    ]),

    # Space
    html.Div(style={'height': '20px'}),

    # Text area for output display
    html.Div(dcc.Textarea(id='output-area', style={'width': '100%', 'height': '200px'}))
])


# Define callback to update the text area based on the submit button click
@app.callback(
    Output('output-area', 'value'),
    Output('input-box', 'value'),
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
        return formatted_messages, input_value
    #return '1', '2'


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
