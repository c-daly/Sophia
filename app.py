# app.py

from dash import Dash
from data.milvus_wrapper import MilvusWrapper
from data.mongo_wrapper import MongoWrapper
import dash_bootstrap_components as dbc

# Initialize the Dash app with optional external stylesheets
# Here, I'm using Dash Bootstrap Components as an example, but you can use any other stylesheets or none at all.
#app = Dash(__name__, suppress_callback_exceptions=False)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# If using Flask sessions, database connections, or other middleware, those would be initialized here.

# Important: If you plan to deploy the app on a web server and don't want to use Flask's development server,
# you'll expose the Flask server object for WSGI applications:
try:
    server = app.server
except Exception as e:
    print(e)
print("Server initialized")
# Any other global configurations or initializations can go here.

