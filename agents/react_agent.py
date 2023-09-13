from openai_model import OpenAIModel
from data.pinecone_wrapper import PineconeWrapper
from daemons.feedback_daemon import FeedbackDaemon
from daemons.decomposition_daemon import DecompositionDaemon
from tasks.task_list import TaskList
from tools.tool import WikipediaTool, CalculatorTool
from openai_model import OpenAIModel
import re
import os
import httpx
from prompts.prompts import REACT_AGENT_PROMPT

class ReactAgent:
    def __init__(self):
        self.action_re = re.compile('^Action: (\w+): (.*)$')
        self.known_actions = {
            "wikipedia": WikipediaTool.invoke,
            "calculate": CalculatorTool.invoke,
            "llm": self.model_completion
        }
        self.prompt = REACT_AGENT_PROMPT
        self.messages = []
        self.model = OpenAIModel("gpt-3.5-turbo")
        self.messages.append({"role": "system", "content": self.prompt})

    def append_message(self, message, role):
        self.messages.append({"role": role, "content": message})

    def model_completion(self, message):
        self.append_message(message, "user")
        completion = self.model.generate_response(messages=self.messages)
        result = completion['content']
        self.append_message(result, "assistant")
        return result
    def user_interaction(self, max_turns=15):
        i = 0
        question = input("User: ")
        while i < max_turns:
            i += 1
            self.append_message(question, "user")
            completion = self.model.generate_response(messages=self.messages)
            result = completion['content']

            self.append_message(result, "assistant")
            print(result)
            actions = [self.action_re.match(a) for a in result.split('\n') if self.action_re.match(a)]
            if actions:
                # There is an action to run
                action, action_input = actions[0].groups()
                if action not in self.known_actions:
                    raise Exception("Unknown action: {}: {}".format(action, action_input))
                print(" -- running {} {}".format(action, action_input))
                observation = self.known_actions[action](action_input)
                print("Observation:", observation)
                next_prompt = "Observation: {}".format(observation)
            else:
                #bot = ChatBot(prompt)
                question = input("User: ")
                i = 0


prompt = """
    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    Use Thought to describe your thoughts about the question you have been asked.
    Use Action to run one of the actions available to you - then return PAUSE.
    Observation will be the result of running those actions.

    Your available actions are:

    calculate:
    e.g. calculate: 4 * 7 / 3
    Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

    wikipedia:
    e.g. wikipedia: Django
    Returns a summary from searching Wikipedia

    Always look things up on Wikipedia if you have the opportunity to do so.

    Example session:

    Question: What is the capital of France?
    Thought: I should look up France on Wikipedia
    Action: wikipedia: France
    PAUSE

    You will be called again with this:

    Observation: France is a country. The capital is Paris.

    You then output:

    Answer: The capital of France is Paris
    """.strip()
