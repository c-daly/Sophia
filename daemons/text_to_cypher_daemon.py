from models.static_openai_wrapper import StaticOpenAIModel
import config
from prompts.prompts import FEEDBACK_AGENT_PROMPT
class TextToCypherDaemon:
    @staticmethod
    def generate_cypher(text):
        config.logger.info(f"Generating Cypher query for text: {text}")
        prompt = f"Generate a Cypher query that merges the information in this text with the existing knowledge graph. The query will be used directly, so it is essential you return just the query, and that the query can be applied directly to a neo4j database.  Input: {text}"
        try:
            response = StaticOpenAIModel.generate_response(messages=[{"role": "user", "content": prompt}])
        except Exception as e:
            config.logger.info(f"Error generating Cypher query: {e}")
        config.logger.info(f"Generated Cypher query: {response['choices'][0]['message']['content']}")
        result = response['choices'][0]['message']['content']
        return result

