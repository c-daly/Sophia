# index.py

from dash import Dash, dcc, html
from app import app
from templates import master, tab1, tab2

# Import and initialize callbacks (just by importing them, they'll get registered to the app)
from callbacks import tab1_callbacks #, tab2_callbacks

app.layout = html.Div([
    # Master layout components (like header, footer, etc.)
    master.header_component,

    # Main content


    master.footer_component,
])

if __name__ == '__main__':
    app.run_server(debug=True)
