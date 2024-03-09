from abc import ABC, abstractmethod


# Abstract base class for an agent
class AbstractAgent(ABC):

    @abstractmethod
    def generate_query_sequence(self, text):
        pass
