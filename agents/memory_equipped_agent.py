from agents.basic_agent import BasicAgent
from memory.standard_memory import StandardMemoryStore
import config

class MemoryEquippedAgent(BasicAgent):
    def __init__(self, memory_store=None):
        if not memory_store:
            self.memory_store = StandardMemoryStore()
        else:
            self.memory_store = memory_store

        super().__init__()

    def generate_query_sequence(self, text):
        response = super().generate_query_sequence(text)
        response_content = response.get("content")
        message = super().format_message(response)
        self.memory_store.record(message)
        config.logger.debug(f"response_content: {response_content}")





