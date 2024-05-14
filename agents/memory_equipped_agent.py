from agents.basic_agent import BasicAgent
from memory.standard_memory_with_embeddings_and_kg import StandardMemoryWithEmbeddingsAndKG
from tools.web_search_tool import WebSearchTool
import config

class MemoryEquippedAgent(BasicAgent):
    def __init__(self, agent_state=None, memory_store=None):
        if not memory_store:
            self.memory_store = StandardMemoryWithEmbeddingsAndKG()
        else:
            self.memory_store = memory_store

        super().__init__()

    def apply_tools(self, text):
        search_result = WebSearchTool.run(text)
        interim_result = [f"title: {result.title}\tdescription: {result.description}\turl: {result.url}\n"for result in search_result]
        #config.logger.info(f"Google Search Results: {interim_result}")
        return "Google Search Results:\n" + ''.join(interim_result)

    def generate_query_sequence(self, text):
        result = self.apply_tools(text)
        self.append_message(result, "system")
        response = super().generate_query_sequence(text)
        #config.logger.info(f"Response: {response}")
        response_dict = response.to_dict()
        response_content = response_dict['choices'][0]['message']['content']
        message = super().format_query_response_pair(response_content)
        self.memory_store.record(message)
        return response_content





