from memory.AbstractMemoryStore import AbstractMemoryStore
from data.mongo_wrapper import MongoWrapper
import config

class StandardMemory(AbstractMemoryStore):
    def __init__(self, data_store=None):
        if not data_store:
            self.data_store = MongoWrapper()
        self.memory = {}

        
    def record(self, data):
        result = self.data_store.insert_interaction(data)
        #config.logger.debug(f"Recorded data: {data}")
        return result.inserted_id

    def query(self, query):
        pass
