from agents.agent_interfaces import AgentState
"""
Class for standardizing responses in the Sophia app
"""
class GenericResponse:
    def __init__(self, state: AgentState, output: str = "", is_done: bool = False):
        self.output = output
        self.state = state
        self.is_done = is_done

