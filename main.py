from exploratory.enhanced_agent import EnhancedAgent
from exploratory.react_agent import ReactAgent


def main_interaction_loop():
    agent = EnhancedAgent()
    print("Welcome to the Enhanced Agent!")
    while True:
        response = agent.user_interaction()
        print(response)

def react_main_interaction_loop():
    agent = ReactAgent()
    print("Welcome to the React Agent!")
    while True:
        response = agent.user_interaction()
        print(response)

if __name__ == "__main__":
    react_main_interaction_loop()