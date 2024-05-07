import langchain
from tools.abstract_tool import AbstractTool
from googlesearch import search

class WebSearchTool(AbstractTool):
    def __init__(self):
        self.name = "Web Search"

    @staticmethod
    def run(query):
        results = search(query, advanced=True)
        return results

    @staticmethod
    def get_name():
        return self.name


