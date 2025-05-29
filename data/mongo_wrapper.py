from pymongo import MongoClient
import os
import pandas as pd
import config
import sys
from pathlib import Path

# Add the config directory to sys.path to import the config module
config_dir = Path(__file__).parent.parent / 'config'
sys.path.insert(0, str(config_dir))
from config import get_config

class MongoWrapper:
    def __init__(self):
        # Use centralized config for MongoDB URL
        self._config = get_config()
        self.db_url = self._config.get("mongo_url")
        self.client = MongoClient(self.db_url)
        self.db = self.client["sophia"]
        self.collection = self.db['interactions']

    def insert_interaction(self, interaction_data):
        #config.logger.debug(f"Inserting interaction data: {interaction_data}")
        try:
            return self.collection.insert_one(interaction_data)
        except Exception as e:
            print(f"Insert Exception: {e}")

    def preprocess_data(self, data_list):
        for doc in data_list:
            # Convert ObjectID to string
            doc["_id"] = str(doc["_id"])
            config.logger.debug(f"doc: {doc}")
            #doc['query'] = doc['messages'][0]['content']
            #config.logger.debug(f"doc['query']: {doc['query']}")
            #doc['view_response'] = 'VIEW'
            # Flatten metadata
            #if 'metadata' in doc:
            #    metadata = doc.pop('metadata')
            #    doc['agent_fitness_rating'] = metadata.get('agent_fitness_rating')
            #    doc['user_fitness_rating'] = metadata.get('user_fitness_rating')

        return data_list
    def fetch_data(self, page_current=0, page_size=10, sort_by=None, filter_query=None):
        """
        Fetch data based on pagination, sorting, and filtering parameters.

        :param page_current: The current page number (zero-indexed).
        :param page_size: The number of records per page.
        :param sort_by: Information on how the data should be sorted.
        :param filter_query: Filtering criteria.
        :return: A list of dictionaries representing the data.
        """
        #skip = page_current * page_size
        skip = 0
        # Sort data if sort_by is provided
        #if sort_by:
        #    sort_column = sort_by[0]['column_id']
        #    sort_direction = pymongo.ASCENDING if sort_by[0]['direction'] == 'asc' else pymongo.DESCENDING
        #    cursor = self.collection.find().sort(sort_column, sort_direction)
        #config.logger.debug(f"Filter query: {filter_query}")
        cursor = self.collection.find(filter_query)

        print(f"Cursor: {cursor}")

        #print(f"Data: {data}")
        data_list = list(cursor)
        processed_data = self.preprocess_data(data_list)
        #config.logger.debug(f"Processed data: {processed_data}")
        #return pd.DataFrame(processed_data)
        return processed_data

    # Add any other necessary methods here, such as methods for inserting data, updating data, etc.

