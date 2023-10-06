from dash import Input, Output, State, callback_context
from app import app  # Import the app instance from app.py
from data.mongo_wrapper import MongoWrapper
import pandas as pd

@app.callback(
    Output("response-modal", "is_open"),
    Output("modal-body", "children"),
    Input("history-datatable", "active_cell"),
    Input("close-modal", "n_clicks"),
    Input("next-record", "n_clicks"),
    Input("prev-record", "n_clicks"),
    State("history-datatable", "data")
)
def toggle_modal(active_cell, close_clicks, next_clicks, prev_clicks, table_data):
    ctx = callback_context

    if not ctx.triggered:
        return False, ""
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "history-datatable" and active_cell:
        row_data = table_data[active_cell["row"]]
        return True, ""

    elif trigger_id == "next-record" and active_cell:
    #    # Navigate to the next record
        next_row_index = (active_cell["row"] + 1) % len(table_data)
        #return True, table_data[next_row_index]["response"]
        return True, ""
    elif trigger_id == "prev-record" and active_cell:
        # Navigate to the previous record
        prev_row_index = (active_cell["row"] - 1) % len(table_data)
        #return True, table_data[prev_row_index]["response"]
        return True, ""

    elif trigger_id == "close-modal":
        return False, ""

@app.callback(
    [Output('history-datatable', 'data'),
     Output('history-datatable', 'tooltip_data')],
    [Input('history-datatable', 'page_current'),
     Input('history-datatable', 'page_size'),
     Input('history-datatable', 'sort_by'),
     Input('history-datatable', 'filter_query')]  # if filtering is enabled
)
def update_table(page_current, page_size, sort_by, filter_query):
    mongo = MongoWrapper()
    #if len(sort_by):
    #    dff = df.sort_values(
    #        [col['column_id'] for col in sort_by],
    #        ascending=[
    #            col['direction'] == 'asc'
    #            for col in sort_by
    #        ],
    #        inplace=False
    #    )
    #else:
    #    dff = df
    data = mongo.fetch_data()

    #tooltip_data = [
    #    {
    #        'response': {'value': doc['response'], 'type': 'markdown'}
    #    }
    #    for doc in data
    #]
    return data, [{}]
    #return dff.iloc[
    #    page_current * page_size: (page_current + 1) * page_size
    #].to_dict('records')

