from models.static_openai_wrapper import StaticOpenAIModel
from data.neo4j_wrapper import Neo4jWrapper
import config
from prompts.prompts import KG_PROMPT, KG_QUERY_PROMPT

"""
     This class is assumed to operate with a language model
     and is responsible both for trasnlating text to cypher,
     but also providing text summaries of query reults.
"""
class TextToCypherDaemon:

    @staticmethod
    def summarize_query_results(results):
        prompt = f"Summarize the results of the query given: {results}"
        config.logger.info(f"Generating summary for prompt: {prompt}")
        response = StaticOpenAIModel.generate_response(messages=[{"role": "system", "content": prompt}])
        return response['choices'][0]['message']['content']

    @staticmethod
    def get_query_relevant_info(query):
        neo = Neo4jWrapper('bolt://neo4j:7687', 'neo4j', 'password')
        prompt = KG_QUERY_PROMPT.format(topic=query)
        response = StaticOpenAIModel.generate_response(messages=[{"role": "system", "content": prompt}])
        query = response['choices'][0]['message']['content']
        results = neo.query(query)
        return results

    @staticmethod
    def generate_cypher(text):
        # First we need to ask the model for a good query
        # to determine what we already know about the topic
        initial_results = TextToCypherDaemon.get_query_relevant_info(text)

        summary = TextToCypherDaemon.summarize_query_results(initial_results)

        config.logger.info(f"Generated summary: {summary}")
        config.logger.info(f"Generated initial results: {initial_results}")

        # Then we can query the database for the information
        # and add that to the prompt we send to the model
        # to get the final query
        prompt = KG_PROMPT.format(user_input=text, existing_data=summary)
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

