import time
from typing import Any

import httpx
from agno.agent import Agent
from google.genai import errors as genai_errors
from pydantic import BaseModel

from backend.llm import LLMConfig, create_llm
from backend.llm.instrumentation import current_agent_name, wrap_model
from backend.tools.adapter import adapt_tool
from backend.tools.base_tool import BaseTool
from backend.utils.config import settings
from backend.utils.exceptions import PipelineError
from backend.utils.logger import get_logger
from backend.utils.prompt_loader import get_prompt
from backend.utils.retry import retry_async

_EXECUTION_INSTRUCTIONS: list[str] = [
    "Use tools only when necessary.",
    "Never repeat the same search.",
    "Do not search for information already retrieved.",
    "Stop searching once sufficient evidence has been collected.",
    "Prefer synthesizing existing information over additional searches.",
    "Do not exceed the available tool budget.",
]


class StartupIQAgent:
    name: str = ""
    _output_model: type[BaseModel] | None = None

    def __init__(
        self,
        tools: list[Any] | None = None,
        output_model: type[BaseModel] | None = None,
        llm_config: LLMConfig | None = None,
        markdown: bool = True,
        extra_instructions: list[str] | None = None,
        tool_call_limit: int | None = None,
    ) -> None:
        if not self.name:
            raise ValueError("StartupIQAgent subclasses must set name")

        self.logger = get_logger(f"agent.{self.name}")
        self._output_model = output_model
        self._tools: list[Any] = []
        self._tool_call_limit = (
            tool_call_limit if tool_call_limit is not None else settings.tool_call_limit
        )
        self._execution_instructions_added = False

        system_message = get_prompt(self.name)

        provider = create_llm(llm_config)

        wrapped = wrap_model(provider.agno_model)
        self.agent = Agent(
            name=self.name,
            model=wrapped,
            system_message=system_message,
            tools=[],
            output_schema=output_model,
            markdown=markdown,
            tool_call_limit=self._tool_call_limit,
            instructions=extra_instructions or [],
        )

        self.logger.info("Tool call limit: %d", self._tool_call_limit)

        if tools:
            self.register_tools(tools)

    def _add_execution_instructions(self) -> None:
        if self._execution_instructions_added:
            return
        self.agent.instructions.extend(_EXECUTION_INSTRUCTIONS)
        self._execution_instructions_added = True
        self.logger.debug("Execution efficiency instructions added")

    def register_tools(self, tools: list[Any]) -> None:
        adapted = []
        for t in tools:
            if isinstance(t, BaseTool):
                adapted.append(adapt_tool(t))
            else:
                adapted.append(t)
        self._tools.extend(adapted)
        self.agent.tools = list(self._tools)
        self._add_execution_instructions()

    async def run_structured(
        self,
        message: str,
        output_model: type[BaseModel] | None = None,
    ) -> BaseModel:
        model = output_model or self._output_model
        if model is None:
            raise ValueError(
                "No output model set. Pass output_model to run_structured() "
                "or provide it in the constructor."
            )

        current_agent_name.set(self.name)
        self.logger.info("Agent %s started", self.name)
        start_time = time.monotonic()

        retryable = (genai_errors.APIError, httpx.HTTPError, ConnectionError, TimeoutError)
        response = await retry_async(
            lambda: self.agent.arun(message, output_schema=model),
            max_retries=3,
            delay=1.0,
            backoff=2.0,
            exceptions=retryable,
        )

        elapsed = time.monotonic() - start_time

        tool_calls_used = _extract_tool_call_count(response)
        self.logger.info(
            "Agent %s finished — Tool calls used: %s/%d — Duration: %.1fs",
            self.name,
            tool_calls_used,
            self._tool_call_limit,
            elapsed,
        )

        content = response.content
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, dict):
            return model.model_validate(content)
        if isinstance(content, str):
            raise PipelineError(
                f"LLM provider returned an error instead of structured output: {content[:300]}"
            )
        raise TypeError(
            f"Expected structured output as {model.__name__}, "
            f"got {type(content).__name__}: {content[:200]}"
        )


def _extract_tool_call_count(response: Any) -> str:
    try:
        metrics = getattr(response, "metrics", None)
        if metrics and isinstance(metrics, dict):
            total = metrics.get("total_tool_calls")
            if total is not None:
                return str(total)
        messages = getattr(response, "messages", None) or []
        count = sum(
            1
            for m in messages
            if getattr(m, "tool_calls", None) or getattr(m, "tool_call_id", None)
        )
        if count > 0:
            return str(count)
    except Exception:
        pass
    return "?"
