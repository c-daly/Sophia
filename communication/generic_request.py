"""
Class for standardizing requests in the Sophia app.
"""
class GenericRequest:
    def __init__(self, content: str, metadata: dict = None):
        """
        Initializes a GenericRequest instance.

        :param content: The content of the request. 
        :param metadata: Optional metadata associated with the request.
        """
        self.content = content
        self.metadata = metadata
