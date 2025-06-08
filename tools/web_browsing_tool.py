# web_browsing_tool.py
import requests
from readability.readability import Document
from agents.agent_interfaces import AgentState
from bs4 import BeautifulSoup
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
        self.cfg.logger.debug(f"WebBrowsingTool: Fetching content from URL: {url}")
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad responses
        
        soup = BeautifulSoup(response.text, 'html.parser')

        #extracted_text = self.extract_text(soup)
        extracted_text = self.extract_clean_main_text(url)
        return GenericResponse(output=extracted_text)

    def extract_text(self, soup):
        #soup = BeautifulSoup(html_content, features="lxml")
        # Remove scripts, styles, and non-visible elements
        for script_or_style in soup(['script', 'style', 'head', 'noscript']):
            script_or_style.extract()
        # Extract visible text
        text = soup.get_text(separator='\n')

        # Break into lines, remove leading/trailing spaces, and filter empty lines
        lines = [line.strip() for line in text.splitlines()]
        human_readable_text = '\n'.join(line for line in lines if line)

        return human_readable_text


    def extract_clean_main_text(self, url):
        response = requests.get(url)
        response.raise_for_status()

        # Use readability to extract main content
        doc = Document(response.text)
        html_content = doc.content()  # this is HTML
        title = doc.title()

        # Convert HTML to plain text
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text(separator='\n')

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        cleaned_text = '\n'.join(line for line in lines if line)

        return title + "\n" + cleaned_text

       
