# web_browsing_tool.py
import requests
from communication.generic_request import GenericRequest
from communication.generic_response import GenericResponse
from tools.abstract_tool import AbstractTool

class WebBrowsingTool(AbstractTool):
    def __init__(self, cfg):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.name = "WebBrowsingTool"
        self.cfg = cfg
        self.description = "A tool to browse the web and retrieve content from a given URL."

    def run(self, request: GenericRequest) -> GenericResponse:
        url = request.content
        response = requests.get(url, headers=self.headers)
        self.cfg.logger.debug(f"Response: {response.text}")
        response.raise_for_status()  # Raise an error for bad responses
        return GenericResponse(self.extract_text(response.text))

    def extract_text(self, html_content):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
