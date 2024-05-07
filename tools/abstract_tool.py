from abc import ABC, abstractmethod

class AbstractTool(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, args=None):
        pass

    @abstractmethod
    def get_name(self):
        pass
