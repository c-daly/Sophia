from openai_model import OpenAIModel
from prompts.prompts import FEEDBACK_AGENT_PROMPT
class FeedbackAgent:
    def __init__(self):
        self.model = OpenAIModel('gpt-3.5-turbo')

    def evaluate_completion(self, query, response, conversation_history):
        # Add the evaluation question to the end of the conversation history
        prompt = FEEDBACK_AGENT_PROMPT.format(query=query, response=response, conversation_history=conversation_history)
        #conversation_history.append({"role": "system", "content": evaluation_query})

        conversation_history = [({"role": "system", "content": prompt})]
        print(f"conversation_history: {conversation_history}")
        feedback = self.model.generate_response(messages=conversation_history)

        # Assuming a binary "yes" or "no" response for simplicity
        if "yes" in feedback.content.lower():
            print(f"Task Complete")
            return True
        else:
            print(f"Task Incomplete: {feedback}")
            return False
