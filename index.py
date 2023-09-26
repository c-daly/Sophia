# index.py
from agents.basic_agent import BasicAgent
from dash import html
from app import app
from templates import master
from callbacks.tab1_callbacks import *
from callbacks.history_callbacks import *
# Import and initialize callbacks (just by importing them, they'll get registered to the app)
theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

app.model = BasicAgent()
app.layout = html.Div([

    # Master layout components (like header, footer, etc.)
    master.header_component,

    # Main content


    master.footer_component,
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
