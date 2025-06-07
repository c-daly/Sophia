"""
thinking_styles.py
──────────────────
Central place for every “how-to-think” strategy Sophia can use.

This module defines various thinking styles that Sophia can use to process user input and generate responses.
It includes strategies like:
- Reflex: A single-pass response generation.
- Reactive: A ReAct loop that allows for tool invocation and observation.
- Reflective: A multi-step process involving drafting, self-critique, and optional revision.
"""

from __future__ import annotations
from enum import Enum
from agents.agent_interfaces import AgentState
from pydantic import BaseModel
from models.abstract_model import AbstractModel
from communication.generic_response import GenericResponse
from logging import Logger


# ──────────────────────────────────────────────────────────────────────────────
#  Shared config & enums
# ──────────────────────────────────────────────────────────────────────────────

class ThinkStyle(str, Enum):
    REFLEX      = "reflex"       # one-shot answer
    REACTIVE    = "reactive"     # ReAct loop (tools)
    REFLECTIVE  = "reflective"   # draft → critic → revise


class CoTVisibility(str, Enum):
    NONE    = "none"     # don’t generate chain-of-thought
    HIDDEN  = "hidden"   # generate but strip before reply
    EXPOSE  = "expose"   # include reasoning in final answer


class ThinkingConfig(BaseModel):
    style: ThinkStyle = ThinkStyle.REFLEX
    temperature: float = 0.1
    max_iterations: int = 3
    cot: CoTVisibility = CoTVisibility.EXPOSE
    model_name: str = "gpt-4o-mini"        # picked by chooser


# ──────────────────────────────────────────────────────────────────────────────
#  Public entry-point
# ──────────────────────────────────────────────────────────────────────────────

def think(
    llm_chat: AbstractModel,
    state: AgentState,
    cfg: ThinkingConfig,
    logger: Logger
    ) -> GenericResponse:
    """
    llm_chat(messages, model_name, temperature) -> str
        Narrow adapter around your OpenAI helper so we can swap in any backend.

    state must expose:
        .input : str
        .tool_runner(name:str, args:dict) -> Any   (only used by REACTIVE)
    """
    if cfg.style is ThinkStyle.REFLEX:
        return _reflex(llm_chat, state, cfg, logger)
    if cfg.style is ThinkStyle.REACTIVE:
        return _reactive(llm_chat, state, cfg, logger)
    if cfg.style is ThinkStyle.REFLECTIVE:
        return _reflective(llm_chat, state, cfg, logger)
    raise ValueError(f"Unknown style: {cfg.style}")


# ──────────────────────────────────────────────────────────────────────────────
#  Strategy implementations
# ──────────────────────────────────────────────────────────────────────────────

def _reflex(llm_chat, state, cfg, logger) -> GenericResponse:
    """Single pass; no chain-of-thought unless cfg.cot != NONE."""
    system_prompt = "Answer the user concisely and accurately."
    if cfg.cot is CoTVisibility.HIDDEN:
        system_prompt = (
            "Think step-by-step internally. "
            "After thinking, output ⧉ANSWER⧉ and your final answer."
        )
    #messages = [
    #    {"role": "system", "content": system_prompt},
    #    {"role": "user",   "content": state.user_msg.content},
    #]

    messages = state.get_messages_for_llm()
    raw = llm_chat.generate_response(messages)
    raw = raw.output.strip()
    if cfg.cot is CoTVisibility.HIDDEN:
        return GenericResponse(state=state, output=raw.split("⧉ANSWER⧉")[-1].strip())
    return GenericResponse(state=state, output=raw)


def _reactive(llm_chat, state, cfg, logger) -> GenericResponse:
    """
    Simple ReAct loop:
        Thought -> (optional) tool call -> Observation … finish.
    """
    messages = [
        {"role": "system", "content":
            "You can think and act in this loop:\n"
            "THOUGHT: ...\n"
            "ACTION: {\"name\": tool_name, \"arguments\": {...}}  # optional\n"
            "OBSERVATION: ...                                    # set by system\n"
            "When you have a complete and correct reply, respond with FINAL: <answer to user>"},
        {"role": "user", "content": state.input.content},
    ]

    for _ in range(cfg.max_iterations):
        assistant = llm_chat.generate_response(messages)
        assistant = assistant.output.strip()
        messages.append({"role": "assistant", "content": assistant})

        logger.debug(f"LLM response: {assistant}")

        # finished?
        if assistant.startswith("FINAL:"):
            return GenericResponse(
                    state=state,
                    output = assistant[len("FINAL:"):].strip(),
            )

        # tool invocation?
        if "ACTION:" in assistant:
            try:
                action_json = assistant.split("ACTION:")[1].strip()
                action = json.loads(action_json)
                result = state.tool_runner(action["name"], action["arguments"])

                logger.debug(f"Tool result: {result}")

                messages.append({"role": "system", "content":
                    f"OBSERVATION: {result}"})
            except Exception as exc:
                messages.append({"role": "system", "content":
                    f"OBSERVATION: tool_error: {exc}"})

    # fallback
    return GenericResponse(
        state=state,
        output="I couldn't complete the task in time. Please try again.",
    )


def _reflective(llm_chat, state, cfg, logger) -> GenericResponse:
    """Draft ➔ self-critique ➔ optional revision.  ≤3 LLM calls."""
    # 1) Draft with hidden CoT
    draft = llm_chat.generate_response(
        [
            {"role": "system", "content":
                "Think step-by-step, then output ⧉ANSWER⧉ and your final answer."},
            {"role": "user", "content": state.user_msg.content},
        ],
    )

    draft = draft.output
    answer = draft.split("⧉ANSWER⧉")[-1].strip()


    # 2) Critique
    critique = llm_chat.generate_response(
        [
            {"role": "system", "content":
                "You are a critic. Identify factual errors, missing info, tone issues. Expand the answer to be more helpful, if necessary."},
            {"role": "assistant", "content": answer},
            {"role": "user", "content": "List issues or reply NONE."},
        ],
    )

    critique = critique.output_text.strip()

    # 3) Optional revision
    if critique != "NONE":
        answer = llm_chat.generate_response(
            [
                {"role": "system", "content":
                    "Revise the answer so it addresses the critique. "
                    "Respond with the improved answer only."},
                {"role": "assistant", "content": answer},
                {"role": "user", "content": f"Critique:\n{critique}"},
            ],
        )

    return GenericResponse(state=state, output=answer.output)

