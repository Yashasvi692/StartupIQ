import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ToolResponse:
    success: bool
    data: Any = None
    error: str | None = None
    duration_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool interface"

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> ToolResponse: ...

    async def run(self, *args: Any, **kwargs: Any) -> ToolResponse:
        start = time.perf_counter()
        try:
            result = await self.execute(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            result.duration_ms = round(elapsed, 2)
            logger.info("Tool '%s' completed in %.2fms", self.name, elapsed)
            return result
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error("Tool '%s' failed after %.2fms: %s", self.name, elapsed, str(e))
            return ToolResponse(
                success=False,
                error=str(e),
                duration_ms=round(elapsed, 2),
            )
