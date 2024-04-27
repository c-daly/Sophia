# app.py

from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Important: If you plan to deploy the app on a web server and don't want to use Flask's development server,
# you'll expose the Flask server object for WSGI applications:
try:
    server = app.server
except Exception as e:
    print(e)
print("Server initialized")

