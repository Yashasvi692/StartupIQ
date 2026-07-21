from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.llm.instrumentation import (
    GeminiTracker,
    _classify_call,
    _try_classify,
    current_agent_name,
    wrap_model,
)


class TestClassifyCall:
    def test_classify_structured_output(self):
        assert (
            _classify_call(response_format={"type": "json"}, retry_with_guidance=False, messages=[])
            == "structured_output"
        )

    def test_classify_repair(self):
        assert (
            _classify_call(response_format=None, retry_with_guidance=True, messages=[]) == "repair"
        )

    def test_classify_tool_call(self):
        msg = MagicMock()
        msg.role = "tool"
        assert (
            _classify_call(response_format=None, retry_with_guidance=False, messages=[msg])
            == "tool_call"
        )

    def test_classify_tool_call_dict(self):
        msg = {"role": "tool", "content": "result"}
        assert (
            _classify_call(response_format=None, retry_with_guidance=False, messages=[msg])
            == "tool_call"
        )

    def test_classify_generate_default(self):
        msg = MagicMock()
        msg.role = "user"
        assert (
            _classify_call(response_format=None, retry_with_guidance=False, messages=[msg])
            == "generate"
        )


class TestTryClassify:
    def test_structured_output_from_kwargs(self):
        cls = _try_classify({"response_format": {"type": "json"}, "messages": []})
        assert cls == "structured_output"

    def test_repair_from_kwargs(self):
        cls = _try_classify({"retry_with_guidance": True, "messages": []})
        assert cls == "repair"

    def test_tool_call_from_kwargs(self):
        cls = _try_classify({"messages": [MagicMock(role="tool")]})
        assert cls == "tool_call"

    def test_generate_from_kwargs(self):
        cls = _try_classify({"messages": [MagicMock(role="user")]})
        assert cls == "generate"

    def test_empty_kwargs_falls_back_to_generate(self):
        cls = _try_classify({})
        assert cls == "generate"


class TestGeminiTracker:
    def test_singleton(self):
        t1 = GeminiTracker.get()
        t2 = GeminiTracker.get()
        assert t1 is t2

    def test_reset_clears_requests(self):
        tracker = GeminiTracker.get()
        tracker.record("test", "generate", "2026-01-01")
        assert len(tracker.requests) == 1
        tracker.reset()
        assert len(tracker.requests) == 0

    def test_record_request(self):
        tracker = GeminiTracker.get()
        tracker.reset()
        tracker.record(
            "agent_x", "tool_call", "2026-01-01T00:00:00", duration=1.5, status="success"
        )
        assert len(tracker.requests) == 1
        r = tracker.requests[0]
        assert r["agent"] == "agent_x"
        assert r["type"] == "tool_call"
        assert r["duration"] == 1.5
        assert r["status"] == "success"

    def test_print_summary_empty(self, capsys):
        tracker = GeminiTracker.get()
        tracker.reset()
        tracker.print_summary()
        captured = capsys.readouterr()
        assert "No Gemini requests recorded" in captured.out

    def test_print_summary_with_data(self, capsys):
        tracker = GeminiTracker.get()
        tracker.reset()
        tracker.record("Research Agent", "generate", "2026-01-01T00:00:00")
        tracker.record("Research Agent", "tool_call", "2026-01-01T00:00:01")
        tracker.record("Competition Agent", "generate", "2026-01-01T00:00:02")
        tracker.print_summary()
        captured = capsys.readouterr()
        assert "Research Agent" in captured.out
        assert "Competition Agent" in captured.out
        assert "Gemini requests: 2" in captured.out
        assert "Total Gemini requests: 3" in captured.out


class TestWrapModelTransparency:
    """Regression: wrapper must forward args/kwargs exactly as received."""

    @pytest.mark.asyncio
    async def test_forward_kwargs_unchanged(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        received: dict = {}

        async def spy_ainvoke(*args, **kwargs):
            received["args"] = args
            received["kwargs"] = kwargs
            return "ok"

        model = MagicMock()
        model.ainvoke = spy_ainvoke
        model.invoke = MagicMock(return_value="ok")
        wrap_model(model)

        msg = MagicMock()
        token = current_agent_name.set("test_agent")
        try:
            result = await model.ainvoke(
                messages=[msg],
                assistant_message=MagicMock(),
                response_format={"type": "json"},
                tools=None,
                tool_choice=None,
                run_response=None,
                compress_tool_results=False,
                retry_with_guidance=False,
            )
        finally:
            current_agent_name.reset(token)

        assert result == "ok"
        assert len(received["args"]) == 0
        assert received["kwargs"]["response_format"] == {"type": "json"}
        assert received["kwargs"]["retry_with_guidance"] is False
        assert received["kwargs"]["messages"] == [msg]

    @pytest.mark.asyncio
    async def test_forward_positional_args_unchanged(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        received: dict = {}

        async def spy_ainvoke(*args, **kwargs):
            received["args"] = args
            received["kwargs"] = kwargs
            return "ok"

        model = MagicMock()
        model.ainvoke = spy_ainvoke
        model.invoke = MagicMock(return_value="ok")
        wrap_model(model)

        a, b, c = MagicMock(), MagicMock(), MagicMock()
        token = current_agent_name.set("test_agent")
        try:
            result = await model.ainvoke(a, b, c)
        finally:
            current_agent_name.reset(token)

        assert result == "ok"
        assert received["args"] == (a, b, c)
        assert len(received["kwargs"]) == 0

    @pytest.mark.asyncio
    async def test_forward_mixed_args_unchanged(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        received: dict = {}

        async def spy_ainvoke(*args, **kwargs):
            received["args"] = args
            received["kwargs"] = kwargs
            return "ok"

        model = MagicMock()
        model.ainvoke = spy_ainvoke
        model.invoke = MagicMock(return_value="ok")
        wrap_model(model)

        a, b = MagicMock(), MagicMock()
        token = current_agent_name.set("test_agent")
        try:
            result = await model.ainvoke(a, b, extra="value")
        finally:
            current_agent_name.reset(token)

        assert result == "ok"
        assert received["args"] == (a, b)
        assert received["kwargs"] == {"extra": "value"}

    def test_forward_invoke_sync_positional(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        received: dict = {}

        def spy_invoke(*args, **kwargs):
            received["args"] = args
            received["kwargs"] = kwargs
            return "ok"

        model = MagicMock()
        model.ainvoke = AsyncMock(return_value="ok")
        model.invoke = spy_invoke
        wrap_model(model)

        a, b = MagicMock(), MagicMock()
        token = current_agent_name.set("test_agent")
        try:
            result = model.invoke(a, b)
        finally:
            current_agent_name.reset(token)

        assert result == "ok"
        assert received["args"] == (a, b)

    def test_forward_invoke_sync_keyword(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        received: dict = {}

        def spy_invoke(*args, **kwargs):
            received["args"] = args
            received["kwargs"] = kwargs
            return "ok"

        model = MagicMock()
        model.ainvoke = AsyncMock(return_value="ok")
        model.invoke = spy_invoke
        wrap_model(model)

        token = current_agent_name.set("test_agent")
        try:
            result = model.invoke(messages=[MagicMock()], tools=None)
        finally:
            current_agent_name.reset(token)

        assert result == "ok"
        assert "messages" in received["kwargs"]
        assert received["kwargs"]["tools"] is None
        assert len(received["args"]) == 0

    @pytest.mark.asyncio
    async def test_wrapper_does_not_swallow_return_value(self):
        async def spy_ainvoke(*args, **kwargs):
            return {"content": "hello"}

        model = MagicMock()
        model.ainvoke = spy_ainvoke
        model.invoke = MagicMock(return_value="ok")
        wrap_model(model)

        token = current_agent_name.set("agent")
        try:
            result = await model.ainvoke(messages=[])
        finally:
            current_agent_name.reset(token)

        assert result == {"content": "hello"}

    @pytest.mark.asyncio
    async def test_wrapper_does_not_swallow_exception(self):
        async def spy_ainvoke(*args, **kwargs):
            raise RuntimeError("original error")

        model = MagicMock()
        model.ainvoke = spy_ainvoke
        model.invoke = MagicMock(return_value="ok")
        wrap_model(model)

        token = current_agent_name.set("agent")
        try:
            with pytest.raises(RuntimeError, match="original error"):
                await model.ainvoke(messages=[])
        finally:
            current_agent_name.reset(token)

    @pytest.mark.asyncio
    async def test_wrapped_ainvoke_records_calls(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        model = MagicMock()
        model.ainvoke = AsyncMock(return_value="response")
        model.invoke = MagicMock(return_value="response")

        wrap_model(model)

        token = current_agent_name.set("test_agent")
        try:
            result = await model.ainvoke(
                messages=[MagicMock()],
                assistant_message=MagicMock(),
                response_format=None,
                tools=None,
                tool_choice=None,
                run_response=None,
                compress_tool_results=False,
                retry_with_guidance=False,
            )
        finally:
            current_agent_name.reset(token)

        assert result == "response"
        assert len(tracker.requests) >= 1
        assert tracker.requests[0]["agent"] == "test_agent"

    @pytest.mark.asyncio
    async def test_wrapped_ainvoke_records_error(self):
        tracker = GeminiTracker.get()
        tracker.reset()

        model = MagicMock()
        model.ainvoke = AsyncMock(side_effect=ValueError("oops"))
        model.invoke = MagicMock(return_value="response")

        wrap_model(model)

        token = current_agent_name.set("err_agent")
        try:
            with pytest.raises(ValueError, match="oops"):
                await model.ainvoke(
                    messages=[MagicMock()],
                    assistant_message=MagicMock(),
                )
        finally:
            current_agent_name.reset(token)

        assert len(tracker.requests) == 1
        assert tracker.requests[0]["agent"] == "err_agent"
        assert "error" in tracker.requests[0]["status"]
