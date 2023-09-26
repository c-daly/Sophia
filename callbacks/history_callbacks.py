from dash import Input, Output, State
from app import app  # Import the app instance from app.py
from data.mongo_wrapper import MongoWrapper
import pandas as pd

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

    tooltip_data = [
        {
            'response': {'value': doc['response'], 'type': 'markdown'}
        }
        for doc in data
    ]
    return data, tooltip_data
    #return dff.iloc[
    #    page_current * page_size: (page_current + 1) * page_size
    #].to_dict('records')

