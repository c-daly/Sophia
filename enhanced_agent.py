from openai_model import OpenAIModel
#from PineconeWrapper import PineconeWrapper
from data.pinecone_wrapper import PineconeWrapper
from daemons.feedback_daemon import FeedbackDaemon
from daemons.decomposition_daemon import DecompositionDaemon
import time
from tasks.task_list import TaskList
import os
from prompts.prompts import MAIN_AGENT_PROMPT, FEEDBACK_AGENT_PROMPT, TOOL_SELECTOR_PROMPT

class EnhancedAgent:
    def __init__(self, model_name="gpt-3.5-turbo", index_name="defaultindex"):
        self.pineconeAPI_KEY = "" #os.environ["PINECONE_API_KEY"]
        self.model = OpenAIModel(model_name)
        self.pinecone = PineconeWrapper(index_name)
        self.conversation_history = []  # Move the conversation history to be an instance variable
        self.feedback_daemon = FeedbackDaemon()
        self.decomposition_daemon = DecompositionDaemon()
        self.tasks = []
        self.task_list = TaskList()

    def user_interaction(self):
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
            if not self.task_list.tasks:
                self.task_list.tasks.append(input("User: "))
            # Generate response based on the conversation history
            user_input = self.task_list.tasks[0]

            # Handle potential task decomposition
            #if self.decomposition_daemon.should_decompose(user_input):
            #    tasks = self.decomposition_daemon.decompose(user_input)
            #    if tasks['content']:
            #        tasks = tasks['content'].split(',')
            #        print(tasks)
            #        self.task_list.prepend_tasks(tasks)
            #    print(self.task_list.tasks)

            # craft message from input
            self.conversation_history.append({"role": "user", "content": user_input})

            # get standard model response
            response = self.model.generate_response(messages=self.conversation_history)

            # append conversation history
            self.conversation_history.append({"role": "assistant", "content": response['content']})

            # Display the model's response
            print(f"Assistant: {response['content']}")

            # Store the interaction as an embedding in Pinecone
            #user_input_embedding = self.model.generate_embedding(user_input)
            #interaction_text = f"User: {user_input}\nAssistant: {response['content']}"
            #embedding = self.model.generate_embedding(interaction_text)
            #timestamp = str(time.time())
            #self.pinecone.add_embedding(embedding=embedding, original_text=interaction_text,
            #                            metadata={"timestamp": timestamp, "weight": 1, "text": interaction_text})

            # Evaluate task completion
            #TASK_COMPLETE = self.feedback_daemon.evaluate_completion(query=user_input, response=response['content'], conversation_history=self.conversation_history)
            #Check if the response warrants further user input
            #if "follow_up_required" in response:  # This is a placeholder condition
            if True:
                print(f"Popping {self.task_list.pop_task_from_start()}\n")
                TASK_COMPLETE = len(self.task_list.tasks) == 0
