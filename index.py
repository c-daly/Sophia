# index.py
import dash
from dash import html
from agents.command_agent import CommandAgent
from app import app
from templates import master
from callbacks.tab1_callbacks import *
from callbacks.history_callbacks import *
import dash_bootstrap_components as dbc

modal = dbc.Modal(
    [
        dbc.ModalHeader("Full Response"),
        dbc.ModalBody(id="modal-body", children=[
            html.Div([
                dcc.Markdown(id='modal-messages', mathjax=True, dangerously_allow_html=True, style={'width': '100%'}),
            ])
        ]),

        dbc.ModalFooter([
            dbc.Button("Prev", id="prev-record", className="ml-auto"),
            dbc.Button("Next", id="next-record", className="ml-right"),
            dbc.Button("Close", id="close-modal", className="ml-left"),
            dbc.Button("Save", id="save-changes", className="ml-left")
        ]),
    ],
    id="response-modal",
)

app.model = CommandAgent()
app.layout = dash.html.Div([

    # Master layout components (like header, footer, etc.)
    master.header_component,

    # Main content


    master.footer_component,
    modal
])

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')
