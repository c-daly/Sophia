from models.static_openai_wrapper import StaticOpenAIModel
import config
from prompts.prompts import KG_PROMPT
class TextToCypherDaemon:
    @staticmethod
    def generate_cypher(text):
        prompt = KG_PROMPT.format(user_input=text)
        config.logger.info(f"Generating Cypher query for text: {prompt}")
        try:
            response = StaticOpenAIModel.generate_response(messages=[{"role": "user", "content": prompt}])
        except Exception as e:
            config.logger.info(f"Error generating Cypher query: {e}")
        config.logger.info(f"Generated Cypher query: {response['choices'][0]['message']['content']}")
        result = response['choices'][0]['message']['content']

        if "cypher" in result.lower():
            result = result.split("cypher")[1]
        return result

