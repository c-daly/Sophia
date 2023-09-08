from openai_model import OpenAIModel
from PineconeWrapper import PineconeWrapper
from FeedbackAgent import FeedbackAgent
import time
from prompts.prompts import MAIN_AGENT_PROMPT, FEEDBACK_AGENT_PROMPT, TOOL_SELECTOR_PROMPT

class EnhancedAgent:
    def __init__(self, model_name="gpt-3.5-turbo", index_name="defaultindex"):
        self.pineconeAPI_KEY = os.environ["PINECONE_API_KEY"]
        self.model = OpenAIModel(model_name)
        self.pinecone = PineconeWrapper(index_name)
        self.conversation_history = []  # Move the conversation history to be an instance variable
        self.feedback_agent = FeedbackAgent()

    def user_interaction1(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        prompt = MAIN_AGENT_PROMPT.format(input_text=conversation_history)
        while True:
            # Generate response based on the conversation history
            response = self.model.generate_response(messages=self.conversation_history, prompt=prompt)
            self.conversation_history.append({"role": "assistant", "content": response['content']})

            # Store the interaction as an embedding in Pinecone
            interaction_text = f"User: {user_input}\nAssistant: {response['content']}"
            embedding = self.model.generate_embedding(interaction_text)
            timestamp = str(time.time())
            self.pinecone.add_embedding(embedding=embedding, original_text=interaction_text,
                                        metadata={"timestamp": timestamp, "weight": 1})

            # Display the model's response
            print(f"Assistant: {response['content']}")

            # Check if the response warrants further user input
            if "follow_up_required" in response:  # This is a placeholder condition
                user_input = input()
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                self.conversation_history.append({"role": "user", "content": user_input})
            else:
                break

    def user_interaction(self):
        user_input = input("User:")
        self.conversation_history.append({"role": "user", "content": user_input})
        user_input_embedding = self.model.generate_embedding(user_input)
        # Query Pinecone for related past interactions
        #related_interactions = self.pinecone.query_embedding(user_input_embedding)
        #if related_interactions:
        #    try:
        #        for interaction in related_interactions.results[0].matches:
        #            self.conversation_history.append(interaction['text'])
        #    except:
        #        pass
        TASK_COMPLETE = False
        while not TASK_COMPLETE:
            # Generate response based on the conversation history
            response = self.model.generate_response(messages=self.conversation_history)
            self.conversation_history.append({"role": "assistant", "content": response['content']})

            # Store the interaction as an embedding in Pinecone
            interaction_text = f"User: {user_input}\nAssistant: {response['content']}"
            embedding = self.model.generate_embedding(interaction_text)
            timestamp = str(time.time())
            self.pinecone.add_embedding(embedding=embedding, original_text=interaction_text,
                                        metadata={"timestamp": timestamp, "weight": 1, "text": interaction_text})
            # Display the model's response
            print(f"Assistant: {response['content']}")
            TASK_COMPLETE = self.feedback_agent.evaluate_completion(query=user_input, response=response['content'], conversation_history=self.conversation_history)
            # Check if the response warrants further user input
            #if "follow_up_required" in response:  # This is a placeholder condition
            if TASK_COMPLETE:
                user_input = input()
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                self.conversation_history.append({"role": "user", "content": user_input})
            else:
                break
