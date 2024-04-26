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
import dash_bootstrap_components as dbc

layout = html.Div([
    html.H3('Conversation View'),

    html.Div([
        dcc.Input(id='input-box', value='', type='text'),
        html.Button('Submit', id='submit-button'),
        html.Div([
            html.Div([

                html.Label('Last Incoming Response:'),
                dcc.Markdown(id='last-response', mathjax=True, style={'width': '100%'}),
            ], style={'width': '50%', 'float': 'left'}),
            html.Div([
                html.Div([
                    html.Label('Last Outgoing Request:'),
                    html.Br(),
                    dcc.Textarea(id='last-request', style={'width': '100%', 'height': '200px'}),
                    html.Br(),
                    html.Label('Conversation History:'),
                    html.Br(),
                    html.Div(dcc.Textarea(id='output-area', style={'width': '100%', 'height': '600px'}))
                ]),
            ], style={'width': '50%', 'float': 'right'}),
        ]),

    ]),
])

