from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

from backend.llm.config import LLMConfig


class LLMProvider(ABC):
    config: LLMConfig

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    @abstractmethod
    async def generate(self, messages: list[dict]) -> str: ...

    @abstractmethod
    async def generate_stream(self, messages: list[dict]) -> AsyncGenerator[str, Any]:
        ...
        if False:  # pragma: no cover
            yield ""
