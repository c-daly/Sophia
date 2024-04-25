from dash import dcc, html, dash_table
from dash.dash_table import DataTable

columns = [
    {"name": "ID", "id": "_id"},
    {"name": "Input Message", "id": "input_message"},
    {"name": "Output Message", "id": "output_message", "hidden": True},
    {"name": "human score", "id": "human_score"},
    #{"name": "agent fitness rating", "id": "agent_fitness_rating"},
    {"name": "Distance", "id": "distance"},
]

layout = html.Div([
    # Title
    html.H3("Interaction History"),

    # Filter Area
    html.Div([
        html.Label("Search:"),
        dcc.Input(id='history-search-input', type='text', placeholder='Enter keywords...'),
        html.Button("Search", id='history-search-button'),
        # Optionally, add a date range picker or other filters here
        # ...
    ], style={'marginBottom': '10px'}),

    # DataTable
    DataTable(
        id='history-datatable',
        columns=columns,
        hidden_columns=['output_message'],
        page_size=10,  # number of rows per page
        #page_action='custom',
        #sort_action='custom',
        sort_mode='multi',
        sort_by=[],
        filter_action='custom',  # enable filtering
        style_table={'overflowX': 'auto'},  # handle wide tables
    ),

    # Data Control Area (if needed)
    html.Div([
        html.Button("Edit", id='edit-button'),
        html.Button("Delete", id='delete-button'),
        html.Button("Export", id='export-button')
    ], style={'marginTop': '10px'})
])

