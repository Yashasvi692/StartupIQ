from collections.abc import AsyncGenerator
from typing import Any

from backend.llm.config import LLMConfig
from backend.llm.provider import LLMProvider
from backend.llm.providers.agno_provider import AgnoProvider

_registry: dict[str, type[LLMProvider]] = {}


def register_provider(name: str, cls: type[LLMProvider]) -> None:
    _registry[name] = cls


def get_provider(name: str) -> type[LLMProvider] | None:
    return _registry.get(name)


register_provider("default", AgnoProvider)


def create_llm(config: LLMConfig | None = None) -> LLMProvider:
    if config is None:
        config = LLMConfig.from_settings()

    provider_cls = get_provider("default")
    if provider_cls is not None:
        return provider_cls(config)

    return _PlaceholderProvider(config)


class _PlaceholderProvider(LLMProvider):
    """Fallback provider when no provider is registered."""

    async def generate(self, messages: list[dict]) -> str:
        raise NotImplementedError(
            "No LLM provider registered. "
            "Install and configure a provider before generating responses."
        )

    async def generate_stream(self, messages: list[dict]) -> AsyncGenerator[str, Any]:
        raise NotImplementedError(
            "No LLM provider registered. "
            "Install and configure a provider before generating responses."
        )
        if False:  # pragma: no cover
            yield ""
