# master.py

import dash_bootstrap_components as dbc
from dash import html, dcc
from templates import tab1, tab2

# Header component
header_component = dbc.Tabs(
    [
        dcc.Tabs([
            dcc.Tab(label='Tab 0', value='tab-1', children=tab1.layout),
            dcc.Tab(label='Tab 1', value='tab-2', children=tab2.layout),
        ]),
    ],
    #brand="My Dash App",
    #color="primary",
    #dark=True,
)

# Footer component
footer_component = html.Div([
    html.Hr(),
    html.P("Footer content goes here."),
])

# Any other shared components can be defined here.
