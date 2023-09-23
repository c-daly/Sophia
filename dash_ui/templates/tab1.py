# tab1.py

from dash import dcc, html

layout = html.Div([
    html.H3('Tab 1 Content'),


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
])

# Additional components specific to Tab 1 can be added here
