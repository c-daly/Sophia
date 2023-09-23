from pymongo import MongoClient
import os
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
