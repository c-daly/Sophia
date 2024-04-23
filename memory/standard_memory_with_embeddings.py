from models.static_openai_wrapper import StaticOpenAIModel
from memory.AbstractMemoryStore import AbstractMemoryStore
from data.mongo_wrapper import MongoWrapper
from data.milvus_wrapper import MilvusWrapper
import config

class StandardMemoryWithEmbeddings(AbstractMemoryStore):
    def __init__(self, data_store=None, embeddings_store=None):
        if not data_store:
            self.data_store = MongoWrapper()
        if not embeddings_store:
            self.embeddings_store = MilvusWrapper()
        self.memory = {}

        
    def record(self, data):
        input_text = data['input_message']
        output_text = data['output_message']
        text = f"{input_text}\n{output_text}"
        mongo_response = self.data_store.insert_interaction(data)
        id = mongo_response.inserted_id
        embedding = StaticOpenAIModel.generate_embedding(text)
        result = self.embeddings_store.insert_vector(embedding, str(id))
        config.logger.debug(f"Inserting embedding for id: {id} result: {result}")
    def query(self, query):
        pass
