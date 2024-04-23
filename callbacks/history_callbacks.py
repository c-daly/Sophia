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
        config.logger.debug(f"active row: {table_data[active_cell['row']]}")
        messages = table_data[active_cell["row"]]["messages"]
        # row_data = table_data[active_cell["row"]]
        # return True, table_data[active_cell["row"]]["messages"]
        """
            Lots of refactoring required here. This branch is properly encoding
            messages, but something about the formatting of the messages, or I
            think displaying in a modal is making mathjax report SVG errors.
            It may have something
            to do with the html display attribute.
            
            Additionally this code is just plain messy and message encoding/decoding
            needs to be its own thing.
        """
        try:
            for message in messages:
                formatted_message = ""
                role = message['role']
                if role == 'user':
                    formatted_message = f"{message['role'].capitalize()}: {message['content']}\n"
                elif role == 'assistant':
                    content = json.loads(message['content'], strict=False)
                    msg_string = content['response'] or content
                    formatted_message = f"{message['role'].capitalize()}: {msg_string}\n"

                formatted_messages.append(formatted_message)
            return_messages = '\n'.join(formatted_messages)
            return True, return_messages
        except Exception as e:
            config.logger.debug(f"Exception: {e}")

    elif trigger_id == "next-record" and active_cell:
        #    # Navigate to the next record
        next_row_index = (active_cell["row"] + 1) % len(table_data)
        messages = table_data[next_row_index]["messages"]
        formatted_messages = '\n'.join([f"[{msg['role'].capitalize()}]: {msg['content']}\n" for msg in messages])
        return True, markdown.markdown(formatted_messages)
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


def format_mongo_doc(doc, distance):
    config.logger.debug(f"doc ID: {doc['_id']}")
    new_doc = {'_id': doc['_id'], 'query': doc['messages'][0]['content']}
    config.logger.debug(f"doc['messages']: {doc['messages']}")
    new_doc['messages'] = doc['messages']
    new_doc['distance'] = distance
    config.logger.debug(f"Messages: {new_doc['messages']}")
    return new_doc


def fetch_similar_interactions(search_query):
    config.logger.debug(f"fetch_similar_interactions called with search_query: {search_query}")
    mongo = config.mongo
    if not config.milvus:
        config.milvus = MilvusWrapper()
    if search_query:
        query_embedding = StaticOpenAIModel.generate_embedding(search_query)
        results = config.milvus.search_vectors(query_embedding)
        ids = []
        distances = []

        for result in results:
            for match in result:
                ids.append(ObjectId(match.id))
                distances.append(match.distance)

        filter_query = {"_id": {"$in": ids}}
        data = mongo.fetch_data(filter_query=filter_query)
        mongo_docs_map = {ObjectId(doc['_id']): doc for doc in data}
        joined_data = []
        for milvus_id, distance in zip(ids, distances):
            mongo_doc = mongo_docs_map.get(ObjectId(milvus_id))
            #if mongo_doc:
            #    formatted_doc = {
            #        "_id": str(mongo_doc['_id']),
            #        "query": mongo_doc.get("query", ""),
            #        "distance": distance,
            #        "messages": mongo_doc.get("messages", "")
            #    }
            joined_data.append(mongo_doc)
        # Sort by distance
        joined_data.sort(key=lambda x: x['distance'])
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
