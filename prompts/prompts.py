# prompts.py
MAIN_AGENT_PROMPT = "You are an assistant. Help the user by answering their questions. Use your knowledge and any tools at your disposal.{conversation_history}"
TOOL_SELECTOR_PROMPT = "Based on the following input, select the most appropriate tool to assist: {input}"
FEEDBACK_AGENT_PROMPT = "Evaluate this: Question is {query}. Answer provided is {response}. Was this a satisfactory answer? Only say 'yes' or 'no'."
