from dash import dcc, html, dash_table
from dash.dash_table import DataTable

columns = [
    {"name": "ID", "id": "_id"},
    #{"name": "Timestamp", "id": "timestamp"},
    {"name": "Query", "id": "query"},
    #{"name": "Response", "id": "response"},
    #{"name": "messages", "id": "messages"},
    #{"name": "human fitness rating", "id": "user_fitness_rating"},
    #{"name": "agent fitness rating", "id": "agent_fitness_rating"},
    {"name": "View Full Response", "id": "view-response", "type": "text"}
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

