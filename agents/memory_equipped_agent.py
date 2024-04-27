from agents.basic_agent import BasicAgent
from memory.standard_memory import StandardMemoryStore
from memory.standard_memory_with_embeddings import StandardMemoryWithEmbeddings
from memory.standard_memory_with_embeddings_and_kg import StandardMemoryWithEmbeddingsAndKG
import config

class MemoryEquippedAgent(BasicAgent):
    def __init__(self, memory_store=None):
        if not memory_store:
            self.memory_store = StandardMemoryWithEmbeddingsAndKG()
        else:
            self.memory_store = memory_store

        super().__init__()

    def generate_query_sequence(self, text):
        response = super().generate_query_sequence(text)
        response_dict = response.to_dict()
        response_content = response_dict['choices'][0]['message']['content']
        config.logger.debug(f"response_content: {response_content}")
        message = super().format_query_response_pair(response_content)
        self.memory_store.record(message)
        return response_content





