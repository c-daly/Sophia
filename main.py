from enhanced_agent import EnhancedAgent

import json
def main_interaction_loop():
    agent = EnhancedAgent()
    print("Welcome to the Enhanced Agent!")
    while True:
        response = agent.user_interaction()
        print(response)

if __name__ == "__main__":
    main_interaction_loop()