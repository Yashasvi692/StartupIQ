from collections.abc import AsyncGenerator
from typing import Any

from agno.models.openrouter import OpenRouter

from backend.llm.config import LLMConfig
from backend.llm.provider import LLMProvider
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AgnoProvider(LLMProvider):
    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self._model = OpenRouter(**config.to_provider_kwargs())

    @property
    def agno_model(self) -> OpenRouter:
        return self._model

    async def generate(self, messages: list[dict]) -> str:
        kwargs = self._build_kwargs()
        response = await self._model.response(messages=messages, **kwargs)
        return response.content or ""

    async def generate_stream(self, messages: list[dict]) -> AsyncGenerator[str, Any]:
        kwargs = self._build_kwargs()
        async for chunk in self._model.response_stream(messages=messages, **kwargs):
            content = getattr(chunk, "content", None) or ""
            if content:
                yield content

    def _build_kwargs(self) -> dict:
        return {}
