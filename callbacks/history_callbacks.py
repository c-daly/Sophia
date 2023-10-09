from dash import Input, Output, State, callback_context
from app import app  # Import the app instance from app.py
from data.mongo_wrapper import MongoWrapper
from data.milvus_wrapper import MilvusWrapper
import pandas as pd
import config
from models.static_openai_wrapper import StaticOpenAIModel

#@app.callback(
#    Output("response-modal", "is_open"),
#    Output("modal-body", "children"),
#    Input("history-datatable", "active_cell"),
#    Input("close-modal", "n_clicks"),
#    Input("next-record", "n_clicks"),
#    Input("prev-record", "n_clicks"),
#    State("history-datatable", "data")
#)
#def toggle_modal(active_cell, close_clicks, next_clicks, prev_clicks, table_data):
#    ctx = callback_context

#    if not ctx.triggered:
#        return False, ""
#    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
#    if trigger_id == "history-datatable" and active_cell:
#        row_data = table_data[active_cell["row"]]
#        return True, ""
#
#    elif trigger_id == "next-record" and active_cell:
#    #    # Navigate to the next record
#        next_row_index = (active_cell["row"] + 1) % len(table_data)
#        #return True, table_data[next_row_index]["response"]
#        return True, ""
#    elif trigger_id == "prev-record" and active_cell:
#        # Navigate to the previous record
#        prev_row_index = (active_cell["row"] - 1) % len(table_data)
#        #return True, table_data[prev_row_index]["response"]
#        return True, ""

#    elif trigger_id == "close-modal":
#        return False, ""

@app.callback(
    [Output('history-datatable', 'data')],
    [Input('history-search-input', 'value'),
     Input('history-search-button', 'n_clicks')]
)
def update_table(search_query, n_clicks):
    mongo = config.mongo
    config.logger.debug(f"update_table called with page_current: search_query: {search_query}, n_clicks: {n_clicks}")
    if n_clicks:
        if not config.milvus:
            config.milvus = MilvusWrapper()

        config.logger.debug(f"update_table called with page_current: search_query: {search_query}, n_clicks: {n_clicks}")
        query_embedding = StaticOpenAIModel.generate_embedding(search_query)
        ids = config.milvus.search_vectors(query_embedding)
        config.logger.debug(f"ids: {ids}")

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
    return [data]
    #return dff.iloc[
    #    page_current * page_size: (page_current + 1) * page_size
    #].to_dict('records')

