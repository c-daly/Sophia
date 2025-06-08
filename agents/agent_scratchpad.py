from typing import List, Dict, Optional

class Scratchpad:
    def __init__(self, cfg):
        self.cfg = cfg
        self.user_intent: Optional[str] = None
        self.tool_results: List[Dict[str, str]] = []
        self.reasoning_steps: List[str] = []
        self.memory_context: Optional[str] = None

    def add_tool_result(self, tool: str, input_text: str, output: str):
        self.cfg.logger.debug(f"Adding tool result: {tool} with input: {input_text} and output: {output}")
        self.tool_results.append({
            'tool': tool,
            'input': input_text,
            'output': output
        })

    def add_reasoning_step(self, step: str):
        self.reasoning_steps.append(step)

    def to_prompt_summary(self) -> str:
        summary = []

        if self.user_intent:
            summary.append(f"User Intent: {self.user_intent}")

        for i, result in enumerate(self.tool_results):
            summary.append(f"Tool {i+1}: {result['tool']} used with input: \"{result['input']}\"\nResult:\n{result['output']}")

        if self.reasoning_steps:
            summary.append("Reasoning Steps:\n" + '\n'.join(f"- {step}" for step in self.reasoning_steps))

        if self.memory_context:
            summary.append(f"Relevant Memory:\n{self.memory_context}")

        res = '\n\n'.join(summary)
        self.cfg.logger.debug(f"Scratchpad Summary:\n{res}")
        return res
