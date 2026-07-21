import contextvars
import time
from collections import defaultdict
from datetime import datetime
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)

current_agent_name: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_agent_name", default="unknown"
)


def _classify_call(response_format: Any, retry_with_guidance: bool, messages: list[Any]) -> str:
    if retry_with_guidance:
        return "repair"
    if response_format is not None:
        return "structured_output"
    if messages:
        for m in messages:
            role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else None)
            if role == "tool":
                return "tool_call"
    return "generate"


def _try_classify(kwargs: dict) -> str:
    response_format = kwargs.get("response_format")
    retry_with_guidance = kwargs.get("retry_with_guidance", False)
    messages = kwargs.get("messages") or []
    return _classify_call(response_format, retry_with_guidance, messages)


class GeminiTracker:
    instance: "GeminiTracker | None" = None

    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []

    @classmethod
    def get(cls) -> "GeminiTracker":
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def reset(self) -> None:
        self.requests.clear()

    def record(
        self,
        agent_name: str,
        call_type: str,
        timestamp: str,
        duration: float | None = None,
        status: str | None = None,
    ) -> None:
        self.requests.append(
            {
                "agent": agent_name,
                "type": call_type,
                "timestamp": timestamp,
                "duration": duration,
                "status": status,
            }
        )

    def print_summary(self) -> None:
        if not self.requests:
            print("\nNo Gemini requests recorded.")
            return

        by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in self.requests:
            by_agent[r["agent"]].append(r)

        print("\n" + "=" * 50)
        print("Gemini API Request Summary")
        print("=" * 50)

        total = 0
        for agent_name in sorted(by_agent.keys()):
            agent_reqs = by_agent[agent_name]
            print(f"\n{agent_name}")
            print(f"  Gemini requests: {len(agent_reqs)}")
            total += len(agent_reqs)

        print(f"\nTotal Gemini requests: {total}")
        print("=" * 50)


def wrap_model(model: Any) -> Any:
    """Wrap a Gemini model's ainvoke/invoke to track all API calls.

    The wrapper is completely transparent — it never modifies inputs, outputs,
    or the method signature. It only records metadata around each call.
    """
    original_ainvoke = model.ainvoke
    original_invoke = model.invoke

    async def instrumented_ainvoke(*args: Any, **kwargs: Any) -> Any:
        agent_name = current_agent_name.get()
        call_type = _try_classify(kwargs)
        timestamp = datetime.now().isoformat(timespec="milliseconds")

        logger.info("[Gemini] %s | %s | %s", agent_name, call_type.upper(), timestamp)

        start = time.monotonic()
        try:
            result = await original_ainvoke(*args, **kwargs)
            elapsed = time.monotonic() - start
            GeminiTracker.get().record(
                agent_name, call_type, timestamp, duration=elapsed, status="success"
            )
            return result
        except Exception as e:
            elapsed = time.monotonic() - start
            GeminiTracker.get().record(
                agent_name,
                call_type,
                timestamp,
                duration=elapsed,
                status=f"error: {type(e).__name__}",
            )
            raise

    def instrumented_invoke(*args: Any, **kwargs: Any) -> Any:
        agent_name = current_agent_name.get()
        call_type = _try_classify(kwargs)
        timestamp = datetime.now().isoformat(timespec="milliseconds")

        logger.info("[Gemini] %s | %s | %s", agent_name, call_type.upper(), timestamp)

        start = time.monotonic()
        try:
            result = original_invoke(*args, **kwargs)
            elapsed = time.monotonic() - start
            GeminiTracker.get().record(
                agent_name, call_type, timestamp, duration=elapsed, status="success"
            )
            return result
        except Exception as e:
            elapsed = time.monotonic() - start
            GeminiTracker.get().record(
                agent_name,
                call_type,
                timestamp,
                duration=elapsed,
                status=f"error: {type(e).__name__}",
            )
            raise

    model.ainvoke = instrumented_ainvoke
    model.invoke = instrumented_invoke

    return model
