from abc import ABC, abstractmethod
from registry import ToolMetadata

class AbstractTool(ABC):
    def __init__(self, name:str, description:str):
        self.name = name 

    @abstractmethod
    def run(self, args=None):
        pass
