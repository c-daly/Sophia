from dash import Input, Output, State, callback_context
from app import app  # Import the app instance from app.py
from data.mongo_wrapper import MongoWrapper
from data.milvus_wrapper import MilvusWrapper
import pandas as pd
import config
from models.static_openai_wrapper import StaticOpenAIModel
import json
import pandas as pd
import markdown
from bson import ObjectId


def format_row(row_data):
    input_message = row_data.get("input_message", "")
    output_message = row_data.get("output_message", "")

    return f"QUERY: {input_message}\n\nRESPONSE: {output_message}"
    
@app.callback(
    Output("response-modal", "is_open"),
    Output("modal-messages", "children"),
    Input("history-datatable", "active_cell"),
    Input("close-modal", "n_clicks"),
    Input("next-record", "n_clicks"),
    Input("prev-record", "n_clicks"),
    State("history-datatable", "data")
)
def toggle_modal(active_cell, close_clicks, next_clicks, prev_clicks, table_data):
    ctx = callback_context
    formatted_messages = []
    if not ctx.triggered:
        return False, ""
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == "history-datatable" and active_cell:

        formatted_message = format_row(table_data[active_cell["row"]])

        #config.logger.debug(f"formatted_message: {formatted_message}")
        return True, formatted_message

    elif trigger_id == "next-record" and active_cell:
        #    # Navigate to the next record
        next_row_index = (active_cell["row"] + 1) % len(table_data)
        messages = table_data[next_row_index]["messages"]

        formatted_message = f"QUERY: {input_message}\n\nRESPONSE: {output_message}"
        return True, formatted_message
    elif trigger_id == "prev-record" and active_cell:
        # Navigate to the previous record
        prev_row_index = (active_cell["row"] - 1) % len(table_data)
        messages = table_data[prev_row_index]["messages"]
        formatted_messages = '\n'.join([f"[{msg['role'].capitalize()}]: {msg['content']}\n" for msg in messages])
        return True, formatted_messages

    elif trigger_id == "close-modal":
        return False, ""
    else:
        return True, "Something went wrong"


def fetch_similar_interactions(search_query):
    #config.logger.debug(f"fetch_similar_interactions called with search_query: {search_query}")
    mongo = config.mongo
    if not config.milvus:
        config.milvus = MilvusWrapper()
    if search_query:
        query_embedding = StaticOpenAIModel.generate_embedding(search_query)
        results = config.milvus.search_vectors(query_embedding)
        ids = []
        distances = []

        #config.logger.debug(f"Results: {results}")
        for result in results:
            for match in result:
                config.logger.debug(f"Match: {match}")
                ids.append(ObjectId(match.id))
                distances.append(match.distance)

        filter_query = {"_id": {"$in": ids}}
        data = mongo.fetch_data(filter_query=filter_query)
        mongo_docs_map = {ObjectId(doc['_id']): doc for doc in data}
        joined_data = []
        for milvus_id, distance in zip(ids, distances):
            mongo_doc = mongo_docs_map.get(ObjectId(milvus_id))
            if mongo_doc:
                config.logger.debug(f"Mongo doc: {mongo_doc}")
                formatted_doc = {
                    "_id": str(mongo_doc['_id']),
                    "input_message": mongo_doc.get("input_message", ""),
                    "output_message": mongo_doc.get("output_message", ""),
                    "distance": distance,
                    "human_score": mongo_doc.get("human_score", ""),
                    #"messages": mongo_doc.get("input_message", "")
                }
            joined_data.append(formatted_doc)
        # Sort by distance
        #joined_data.sort(key=lambda x: x['distance'])
        data = joined_data
    else:
        data = mongo.fetch_data()
    return [data]

# TODO: Serious cleanup and refactoring required here
@app.callback(
    [Output('history-datatable', 'data')],
    [Input('history-search-input', 'value'),
     Input('history-search-button', 'n_clicks')]
)
def update_table(search_query, n_clicks):
    # This method should really have a lot more
    # UI related functionality, but it's just
    # not a priority right now.
    return fetch_similar_interactions(search_query)
    #pass
