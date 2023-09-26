# tab1.py
import dash
import time
from dash import dcc, html
from dash.dependencies import Input, Output
from agents.basic_agent import BasicAgent
from app import app
#from data.pinecone_wrapper import PineconeWrapper
from data.mongo_wrapper import MongoWrapper
from data.milvus_wrapper import MilvusWrapper
from models.static_openai_wrapper import StaticOpenAIModel
from dash import dcc, html

layout = html.Div([
    html.H3('Tab 1 Content'),


    # Space
    html.Div(style={'height': '20px'}),

    # Request and Response Textareas on the left
    # Text input component and submit button
    html.Div([
        dcc.Input(id='input-box', value='', type='text'),
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
        html.Div(dcc.Textarea(id='output-area', style={'marginLeft': '20px', 'width': '40%', 'height': '600px'}))
    ]),
])
