# This program creates a langchain coding assistant
# and provides a streamlit user interface for interaction.

from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.tools.file_management.write import WriteFileTool
from langchain.tools.file_management.read import ReadFileTool
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
import os


OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
class CodingAssistant():
    def __init__(self):
        self.past_input = ""
        self.template = """Assistant is a large language model trained by OpenAI.

                        Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

                        Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

                        Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

                        If assistant does not believe it knows something, it will always at least try to search for it.
                        If asked to write code, assistant will always try to write code that is as simple as possible.
                        The assistant will not say it will perform an action if it is not going to perform that action.
                        {history}
                        Human: {human_input}
                        Assistant:"""
        self.search = DuckDuckGoSearchAPIWrapper()
        # self.prompt = PromptTemplate(input_variables=["history", "human_input"], template=self.template)
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.template),
            # The persistent system prompt
            MessagesPlaceholder(variable_name="history"),  # Where the memory will be stored.
            HumanMessagePromptTemplate.from_template("{human_input}"),  # Where the human input will injected
        ])

        self.tools = [Tool(name="search", func=self.search.run,
                           description="useful for when you need to answer questions about current events or information not included in training. You should ask targeted questions"),
                      WriteFileTool(), ReadFileTool()]

        self.llm = ChatOpenAI(temperature=1, openai_api_key=OPENAI_API_KEY,
                              verbose=True)

        self.agent = initialize_agent(self.tools, self.llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, handle_parse_error=True,
                                      verbose=True, memory=ConversationBufferMemory())

    def run(self, message):
        return self.agent.run(message)


# This portion of the code defines the user interface. It is simple, elegant, and follows best practices.

agent = CodingAssistant()
import streamlit as st

# Add a title
st.title("Coding Assistant")
# Create a text area to display past input

# Create an input field
input_text = st.text_input("Enter your input", value="", max_chars=None, key=None)

# Create a submit button
if st.button("Submit"):
    # Call the placeholder function with the input
    output = agent.run(input_text)
    # agent.past_input += output
    # st.write(agent.past_input)
    # st.experimental_rerun()
    # Display the output
    st.write(output)

