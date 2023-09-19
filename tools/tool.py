from abc import ABC, abstractmethod
import httpx
from models.static_openai_wrapper import StaticOpenAIModel

# Define the abstract base class for all tools
class Tool(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def invoke(self, query):
        """Invoke the tool with a specific query and get the result."""
        pass


class DecompositionTool(Tool):
    def __init__(self, threshold=0.7):
        # Threshold for deciding when to decompose
        self.threshold = threshold

    def get_decomp_likelihood(self, input):
        messages = [{"role": "system",
                     "content": 'You are an expert system, adept at decomposing problems into smaller parts.'},
                    {"role": "user", "content": input},
                    {"role": "assistant", "content": 'I need to assign a probability to the likelihood that this problem would be most efficiently solved by decomposing it into smaller parts. It is imperative that my only response is a single floating point number between 0 and 1.'}]
        response_obj = StaticOpenAIModel.generate_response(messages=messages)
        print(f"Decomp likelihood: {response_obj}")
        return response_obj
    def invoke(self, input):
        # Mocked call to the model to get percentage likelihood of decomposition
        decomposition_likelihood = float(self.get_decomp_likelihood(input))


        print(f"Decomposition likelihood: {decomposition_likelihood}")
        # If likelihood is above threshold, prime for decomposition
        if decomposition_likelihood > self.threshold:
            prompt = f"I need to generate as small with three or fewer items that can solve this problem most efficiently. These must be tasks I am capable of performing myself.  Please return the tasks themselves as a comma-separated list of single-quoted strings.  Please return no other text, which would include numbering and newline characters. Use this format: <task1>, <task2>, <task3>.  Here is the task {input}"
            messages = [{"role": "system", "content": prompt}]
            response_obj = StaticOpenAIModel.generate_response(messages=messages)
            return response_obj
        return None

    def mock_model_call(self, input):
        # Mocked function to simulate a call to the LLM and get a percentage
        # In reality, you'd replace this with an actual call and processing
        return random.uniform(0, 1)  # Random float between 0 and 1

# Define the SearchTool derived from the Tool ABC
class SearchTool(Tool):
    def __init__(self, model, prompt="Search the web for: {query}"):
        super().__init__(model)
        self.prompt = prompt

    def invoke(self, query):
        # Mocking the search functionality here; in a real environment, this would involve actual web search logic
        # The prompt can be used to provide more context to the LLM or any other search mechanism
        return f"Web search results for '{query}' would be displayed here."

class WikipediaTool:
    def invoke(query):
        return httpx.get("https://en.wikipedia.org/w/api.php", params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }).json()["query"]["search"][0]["snippet"]

class CalculatorTool:
    def invoke(query):
        return eval(query)
# Example usage
#search_tool = SearchTool(None)  # Passing None for the model since it's not used in this mock example
#search_result = search_tool.invoke("current weather in New York")

#search_result
