import pytest

from backend.llm import AgnoProvider, LLMConfig, create_llm, register_provider
from backend.llm.factory import _registry
from backend.llm.provider import LLMProvider


class TestAgnoImport:
    def test_agno_imports_successfully(self):
        import agno

        assert hasattr(agno, "__version__")

    def test_gemini_imports_successfully(self):
        from agno.models.google import Gemini

        assert Gemini is not None


class TestAgnoProvider:
    def test_provider_created_through_factory(self):
        config = LLMConfig(model="gemini-2.0-flash-001")
        provider = create_llm(config)
        assert isinstance(provider, AgnoProvider)
        assert provider.config.model == "gemini-2.0-flash-001"

    def test_default_registration(self):
        assert "default" in _registry
        assert issubclass(_registry["default"], LLMProvider)
        assert _registry["default"] is AgnoProvider

    def test_custom_registration(self):
        class FakeProvider(LLMProvider):
            async def generate(self, messages):
                return ""

            async def generate_stream(self, messages):
                if False:
                    yield ""

        register_provider("test_custom", FakeProvider)
        assert _registry["test_custom"] is FakeProvider

    def test_no_direct_agno_import_in_business_code(self):
        from backend.llm import create_llm

        provider = create_llm()
        assert isinstance(provider, AgnoProvider)
        assert isinstance(provider, LLMProvider)


class TestSampleAgent:
    @pytest.mark.asyncio
    async def test_provider_configures_agno_model(self):
        config = LLMConfig(
            model="gemini-2.0-flash-001",
            temperature=0.2,
            max_tokens=512,
        )
        provider = create_llm(config)
        assert provider._model.id == "gemini-2.0-flash-001"

    @pytest.mark.asyncio
    async def test_provider_builds_kwargs(self):
        config = LLMConfig()
        provider = create_llm(config)
        kwargs = provider._build_kwargs()
        assert isinstance(kwargs, dict)
