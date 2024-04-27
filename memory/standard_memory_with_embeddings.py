from data.milvus_wrapper import MilvusWrapper
from models.static_openai_wrapper import StaticOpenAIModel
from memory.AbstractMemoryStore import AbstractMemoryStore
from memory.standard_memory import StandardMemory
import config

class StandardMemoryWithEmbeddings(AbstractMemoryStore):
    def __init__(self, embeddings_store=None):
       self.memory = StandardMemory() 
       if not embeddings_store:
           self.embeddings_store = MilvusWrapper() 
        
    def record(self, data):
        id = self.memory.record(data)
        text = f"{data['input_message']}\n{data['output_message']}"
        embedding = StaticOpenAIModel.generate_embedding(text)
        result = self.embeddings_store.insert_vector(embedding, str(id))
        return id

    def query(self, query):
        pass
