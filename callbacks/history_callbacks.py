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
        messages = table_data[active_cell["row"]]["messages"]
        #row_data = table_data[active_cell["row"]]
        #return True, table_data[active_cell["row"]]["messages"]
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

@app.callback(
    [Output('history-datatable', 'data')],
    [Input('history-search-input', 'value'),
     Input('history-search-button', 'n_clicks')]
)
def update_table(search_query, n_clicks):
    mongo = config.mongo
    config.logger.debug(f"update_table called with page_current: search_query: {search_query}, n_clicks: {n_clicks}")
    data = mongo.fetch_data()
    if n_clicks:
        if not config.milvus:
            config.milvus = MilvusWrapper()

        config.logger.debug(f"update_table called with page_current: search_query: {search_query}, n_clicks: {n_clicks}")
        query_embedding = StaticOpenAIModel.generate_embedding(search_query)
        ids = config.milvus.search_vectors(query_embedding)
        config.logger.debug(f"ids: {ids}")
        #data = mongo.fetch_data()
        #df = pd.DataFrame(data)
        #queries = df['messages']  # .apply(lambda x: x[1]['content'])
        #config.logger.debug(f"queries: {df}, type: {type(df)}")


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

