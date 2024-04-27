from memory.AbstractMemoryStore import AbstractMemoryStore
from data.mongo_wrapper import MongoWrapper

class StandardMemory(AbstractMemoryStore):
    def __init__(self, data_store=None):
        if not data_store:
            self.data_store = MongoWrapper()
        self.memory = {}

        
    def record(self, data):
        self.data_store.insert_interaction(data)

    def query(self, query):
        pass
