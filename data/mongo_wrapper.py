import pymongo
from pymongo import MongoClient
import pandas as pd
import os
import bson
class MongoWrapper:
    def __init__(self):
        self.db_url = os.environ["MONGO_URL"]
        self.client = MongoClient(self.db_url)
        self.db = self.client["sophia"]
        self.collection = self.db['interactions']

    def insert_interaction(self, interaction_data):
        try:
            return self.collection.insert_one(interaction_data)
        except Exception as e:
            print(f"Insert Exception: {e}")

    def preprocess_data(self, data_list):
        for doc in data_list:
            # Convert ObjectID to string
            doc["_id"] = str(doc["_id"])

            doc['view_response'] = 'VIEW'
            # Flatten metadata
            if 'metadata' in doc:
                metadata = doc.pop('metadata')
                doc['agent_fitness_rating'] = metadata.get('agent_fitness_rating')
                doc['user_fitness_rating'] = metadata.get('user_fitness_rating')

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
        #else:
        cursor = self.collection.find()

        print(f"Cursor: {cursor}")
        # Handle filtering here if filter_query is provided (optional)
        # ...

        # Fetch the relevant subset of data
        #print(f"Data: {data}")
        data_list = list(cursor)
        processed_data = self.preprocess_data(data_list)
        return processed_data

    # Add any other necessary methods here, such as methods for inserting data, updating data, etc.

