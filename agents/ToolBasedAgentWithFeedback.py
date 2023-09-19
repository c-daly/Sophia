from openai_model import OpenAIModel
from models.static_openai_wrapper import StaticOpenAIModel
from tools.tool import DecompositionTool
from tasks.task_list import TaskList
class ToolBasedAgentWithFeedback:

    def __init__(self):
        # Initialize tools and memory
        #self.tools = [DecompositionTool()]  # Add other tools as needed
        self.messages = []
        self.prompt = "I need to think this through step by step."
        self.task_list = TaskList()
        self.decomposition_allowed = True
        self.nested_decomposition_limit = 3
        self.current_nesting_level = 0

    def process_input(self, user_input):
        #for tool in self.tools:
        #    output = tool.invoke(user_input)
        #    if output:
        #        return output

        # If no tool can handle the input, send to LLM
        return self.call_llm(user_input)

    def call_llm(self, input):
        # Send input to LLM and get response
        # For the sake of this example, we'll mock this
        return f"LLM Response for: {input}"

    def append_message(self, message, role):
        #if len(self.messages) == 0:
            #self.messages.append({"role": "system", "content": self.prompt})
        self.messages.append({"role": role, "content": message})

    def user_interaction(self):
        question = input("User: ")
        while True:
            self.append_message(question, "user")
            completion = StaticOpenAIModel.generate_response(messages=self.messages)
            result = completion['content']

            self.append_message(result, "assistant")
            print(result)

    def generate_completion(self, text):
        try:
            current_response = []
            response = None
            final_response = "There was an error obtaining a response from the model."
            if not self.task_list.tasks:
                self.task_list.tasks = [text]
            while self.task_list.tasks:
                print(self.task_list.tasks)
                if self.decomposition_allowed and self.current_nesting_level < self.nested_decomposition_limit:
                    dt = DecompositionTool()
                    if self.task_list.tasks:
                        task = self.task_list.pop_task_from_start()
                        new_tasks = dt.invoke(task)
                        print(f"New tasks: {new_tasks}")
                        self.current_nesting_level += 1
                        if new_tasks:
                            new_task_list = [task for task in new_tasks.split(',')]
                            self.task_list.prepend_tasks(new_task_list)
                        else:
                            self.task_list.prepend_tasks(task)
                    else:
                        tasks = dt.invoke(text)
                        self.current_nesting_level += 1
                        task_list = [task for task in tasks.split(',')]
                        self.task_list.tasks = task_list
                task = self.task_list.pop_task_from_start()
                print(f"Current task: {task}, remaining tasks: {self.task_list.tasks}")
                self.append_message(text, "user")
                self.append_message("I should think this through step by step.", "assistant")
                response = StaticOpenAIModel.generate_response(self.messages)
                current_response.append(response)
                self.append_message(response, "assistant")
                print(response)

            final_response = StaticOpenAIModel.generate_response(f"I must carefully summarize the following information, careful to omit no information, but also not to repeat myself.  Here is the text to summarize: TEXT: '{current_response}'")
            final_response = response
            print(final_response)
        except Exception as e:
            print(e)
        return final_response
