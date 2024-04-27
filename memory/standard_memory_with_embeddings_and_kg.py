from memory.AbstractMemoryStore import AbstractMemoryStore
from memory.kg_memory import KGMemory
from memory.standard_memory_with_embeddings import StandardMemoryWithEmbeddings
import config

class StandardMemoryWithEmbeddingsAndKG(AbstractMemoryStore):
    def __init__(self):
        self.memory = StandardMemoryWithEmbeddings()
        self.kg_memory = KGMemory()
        
    def record(self, data):
        self.memory.record(data)
        self.kg_memory.record(data)

    def query(self, query):
        pass
