import pytest

from backend.tools.adapter import adapt_tool, adapt_tools
from backend.tools.base_tool import BaseTool, ToolResponse


class TestToolAdapterFailure:
    def test_adapted_tool_raises_on_failure(self):
        class FailingTool(BaseTool):
            name = "failer"
            description = "Always fails"

            async def execute(self, **kw):
                return ToolResponse(success=False, error="Something broke")

        tool = FailingTool()
        adapted = adapt_tool(tool)

        async def run_adapted():
            result = await adapted()
            return result

        with pytest.raises(RuntimeError, match="Something broke"):
            import asyncio

            asyncio.run(run_adapted())

    def test_adapted_tool_with_custom_error_message(self):
        class CustomFailTool(BaseTool):
            name = "custom_fail"
            description = "Fails with custom message"

            async def execute(self, **kw):
                return ToolResponse(success=False, error="Custom failure: rate limited")

        tool = CustomFailTool()
        adapted = adapt_tool(tool)

        async def run_adapted():
            return await adapted()

        with pytest.raises(RuntimeError, match="Custom failure: rate limited"):
            import asyncio

            asyncio.run(run_adapted())

    def test_adapted_tool_passes_kwargs(self):
        class EchoTool(BaseTool):
            name = "echo"
            description = "Echoes input"

            async def execute(self, value="", **kw):
                return ToolResponse(success=True, data=value)

        tool = EchoTool()
        adapted = adapt_tool(tool)

        async def run_adapted():
            result = await adapted(value="hello")
            return result

        import asyncio

        result = asyncio.run(run_adapted())
        assert result == "hello"

    def test_adapt_tool_preserves_name_and_doc(self):
        class MyTool(BaseTool):
            name = "my_tool"
            description = "My custom tool"

            async def execute(self, **kw):
                return ToolResponse(success=True, data="ok")

        tool = MyTool()
        adapted = adapt_tool(tool)
        assert adapted.__name__ == "my_tool"
        assert adapted.__doc__ == "My custom tool"


class TestToolResponseEdgeCases:
    def test_default_duration_ms_is_none(self):
        resp = ToolResponse(success=True, data="test")
        assert resp.duration_ms is None

    def test_default_metadata_is_empty(self):
        resp = ToolResponse(success=True, data="test")
        assert resp.metadata == {}

    def test_custom_metadata(self):
        resp = ToolResponse(success=True, data="test", metadata={"source": "web"})
        assert resp.metadata["source"] == "web"

    def test_error_response_no_data(self):
        resp = ToolResponse(success=False, error="error msg")
        assert resp.data is None
        assert resp.error == "error msg"

    def test_success_response_no_error(self):
        resp = ToolResponse(success=True, data=[1, 2, 3])
        assert resp.error is None

    def test_duration_ms_set_after_run(self):
        class QuickTool(BaseTool):
            name = "quick"
            description = "Quick tool"

            async def execute(self, **kw):
                return ToolResponse(success=True, data="done")

        import asyncio

        tool = QuickTool()
        result = asyncio.run(tool.run())
        assert result.duration_ms is not None
        assert result.duration_ms > 0


class TestToolAdapterBatch:
    def test_adapt_tools_empty_list(self):
        adapted = adapt_tools([])
        assert adapted == []

    def test_adapt_tools_rejects_non_base_tool(self):
        with pytest.raises(TypeError):
            adapt_tool("not_a_tool")


class TestBaseToolEdgeCases:
    @pytest.mark.asyncio
    async def test_run_catches_exception(self):
        class CrashTool(BaseTool):
            name = "crash"
            description = "Crashes on execute"

            async def execute(self, **kw):
                msg = "unexpected crash"
                raise RuntimeError(msg)

        tool = CrashTool()
        result = await tool.run()
        assert result.success is False
        assert "unexpected crash" in result.error
        assert result.duration_ms is not None

    @pytest.mark.asyncio
    async def test_run_sets_duration(self):
        class SlowTool(BaseTool):
            name = "slow"
            description = "Slow tool"

            async def execute(self, **kw):
                import asyncio

                await asyncio.sleep(0.01)
                return ToolResponse(success=True, data="slow result")

        tool = SlowTool()
        result = await tool.run()
        assert result.success is True
        assert result.duration_ms is not None
        assert result.duration_ms >= 1
