#This class is an abstract base class for
# agent memory stores. It provides a common
# interface for all memory stores.

from abc import ABC, abstractmethod

class AbstractMemoryStore(ABC):
    @abstractmethod
    def record(data):
        pass

    def query(query):
        pass
