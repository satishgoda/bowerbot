# Copyright 2026 Binary Core LLC
# SPDX-License-Identifier: Apache-2.0

"""AgentRuntime — the 'Architect' layer.

Handles LLM interaction with the 3D-native system prompt.
Runs a tool-calling loop: LLM decides what to do, we execute it,
feed results back, repeat until the LLM gives a final answer.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import litellm

from bowerbot.config import Settings
from bowerbot.skills.registry import SkillRegistry
from bowerbot.token_manager import TokenManager

logger = logging.getLogger(__name__)

# Core system prompt — always present. Skill-specific prompts are appended.
CORE_PROMPT = """\
You are BowerBot, an expert 3D scene assembly agent that creates OpenUSD scenes
from natural language descriptions.

You help users build 3D scenes by searching for assets, placing them in a USD stage,
and packaging the result. You follow the user's instructions — they decide what to
search, where to place things, and how to organize the scene hierarchy.

When the user gives you a task, use the available tools to accomplish it.
Be specific about what you did and report results clearly.
"""

MAX_TOOL_ROUNDS = 10
MAX_VALIDATION_RETRIES = 2


@dataclass
class AgentRuntime:
    """Layer 1: The Architect."""

    settings: Settings
    skill_registry: SkillRegistry
    conversation_history: list[dict[str, Any]] = field(default_factory=list)
    _system_prompt: str = field(default="", init=False)
    _token_manager: TokenManager = field(init=False)

    def __post_init__(self) -> None:
        """Build the full system prompt from core + active skill prompts."""
        skill_prompts = self.skill_registry.get_skill_prompts()
        if skill_prompts:
            self._system_prompt = CORE_PROMPT + "\n\n" + skill_prompts
        else:
            self._system_prompt = CORE_PROMPT

        self._token_manager = TokenManager(self.settings.llm)

        logger.info(f"System prompt: {len(self._system_prompt)} chars from {self.skill_registry.skill_count} skill(s)")

    async def process(self, user_message: str) -> str:
        """Process a user message through the full tool-calling loop."""
        self.conversation_history.append({"role": "user", "content": user_message})

        tools = self.skill_registry.get_all_tools()
        validation_retries = 0

        for round_num in range(MAX_TOOL_ROUNDS):
            logger.info(f"Agent loop round {round_num + 1}")

            messages, usage = await self._token_manager.prepare_messages(
                self._system_prompt, self.conversation_history,
            )

            kwargs: dict[str, Any] = {
                "model": self.settings.llm.model,
                "messages": messages,
                "max_tokens": self.settings.llm.max_tokens,
                "temperature": self.settings.llm.temperature,
                "num_retries": self.settings.llm.num_retries,
                "timeout": self.settings.llm.request_timeout,
            }

            api_key = self.settings.get_api_key()
            if api_key:
                kwargs["api_key"] = api_key

            if tools:
                kwargs["tools"] = tools

            response = await litellm.acompletion(**kwargs)
            choice = response.choices[0]
            message = choice.message

            if message.tool_calls:
                logger.info(f"LLM requested {len(message.tool_calls)} tool call(s)")

                self.conversation_history.append(message.model_dump())

                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing tool: {func_name}({func_args})")

                    result = await self.skill_registry.execute_tool(func_name, func_args)

                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            result.data if result.success else {"error": result.error}
                        ),
                    })

                # Nudge the LLM to auto-fix validation errors
                self._nudge_on_validation_errors(
                    message.tool_calls, validation_retries,
                )

                continue

            content = message.content or ""
            self.conversation_history.append({"role": "assistant", "content": content})
            return content

        return "Reached maximum tool-calling rounds. Please try a simpler request."

    def _nudge_on_validation_errors(
        self,
        tool_calls: list,
        retries: int,
    ) -> None:
        """If validate_scene returned errors, nudge the LLM to fix them."""
        for tool_call in tool_calls:
            if tool_call.function.name != "assembly__validate_scene":
                continue

            # Find the matching tool result
            for msg in reversed(self.conversation_history):
                if msg.get("tool_call_id") == tool_call.id:
                    try:
                        content = json.loads(msg["content"])
                    except (json.JSONDecodeError, TypeError):
                        break

                    if (
                        not content.get("is_valid", True)
                        and retries < MAX_VALIDATION_RETRIES
                    ):
                        self.conversation_history.append({
                            "role": "user",
                            "content": (
                                "The scene has validation errors. "
                                "Please fix the issues listed above, "
                                "then call validate_scene again."
                            ),
                        })
                        logger.info(
                            f"Validation retry nudge "
                            f"({retries + 1}/{MAX_VALIDATION_RETRIES})"
                        )
                    break

    def reset(self) -> None:
        """Clear conversation history for a new session."""
        self.conversation_history.clear()
