# tab1_callbacks.py

from dash import Input, Output, State
from app import app  # Import the app instance from app.py


# Callback to update the graph based on the user's input
@app.callback(
    Output('tab1-graph', 'figure'),  # 'tab1-graph' is the ID of the graph component in tab1.py
    Input('tab1-submit-button', 'n_clicks'),  # 'tab1-submit-button' is the ID of the submit button in tab1.py
    State('tab1-input', 'value')  # 'tab1-input' is the ID of the input component in tab1.py
)
def update_graph(n_clicks, input_value):
    # For this example, we're just using a dummy logic to update the graph.
    # In a real-world scenario, you might fetch data from a database, perform computations, etc.

    if n_clicks is None:
        # If the button hasn't been clicked, we don't update anything
        return dash.no_update

    # Create a simple figure based on the input value
    figure = {
        'data': [{
            'x': [1, 2, 3],
            'y': [int(input_value) * i for i in [1, 2, 3]],  # Multiply input value with each x coordinate
            'type': 'bar'
        }],
        'layout': {
            'title': f"Graph for Input Value: {input_value}"
        }
    }

    return figure

# Additional callbacks specific to Tab 1 can be defined here
