from abc import ABC, abstractmethod
from communication.generic_request import GenericRequest
from communication.generic_response import GenericResponse

class AbstractTool(ABC):
    def __init__(self, name:str, description:str):
        self.name = name 
        self.description = description

    @abstractmethod
    def run(self, request: GenericRequest) -> GenericResponse:
        pass
