from typing import Any

from agno.agent import Agent
from pydantic import BaseModel

from backend.llm import LLMConfig, create_llm
from backend.tools.adapter import adapt_tool
from backend.tools.base_tool import BaseTool
from backend.utils.logger import get_logger
from backend.utils.prompt_loader import get_prompt


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
    ) -> None:
        if not self.name:
            raise ValueError("StartupIQAgent subclasses must set name")

        self.logger = get_logger(f"agent.{self.name}")
        self._output_model = output_model
        self._tools: list[Any] = []

        system_message = get_prompt(self.name)

        provider = create_llm(llm_config)

        self.agent = Agent(
            name=self.name,
            model=provider.agno_model,
            system_message=system_message,
            tools=[],
            output_schema=output_model,
            markdown=markdown,
            instructions=extra_instructions or [],
        )

        if tools:
            self.register_tools(tools)

    def register_tools(self, tools: list[Any]) -> None:
        adapted = []
        for t in tools:
            if isinstance(t, BaseTool):
                adapted.append(adapt_tool(t))
            else:
                adapted.append(t)
        self._tools.extend(adapted)
        self.agent.tools = list(self._tools)

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

        response = await self.agent.arun(message, output_schema=model)

        content = response.content
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, dict):
            return model.model_validate(content)
        raise TypeError(
            f"Expected structured output as {model.__name__}, "
            f"got {type(content).__name__}: {content}"
        )
