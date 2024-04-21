# master.py

import dash_bootstrap_components as dbc
from dash import html, dcc
from templates import tab1, history_tab

# Header component
header_component = dbc.Tabs(
    [
        dcc.Tabs([
            dcc.Tab(label='Conversations', value='tab-1', children=tab1.layout),
            dcc.Tab(label='History', value='tab-2', children=history_tab.layout),
        ]),
    ],
)

# Footer component
footer_component = html.Div([
    html.Hr(),
    html.P("Footer content goes here."),
])

# Any other shared components can be defined here.
