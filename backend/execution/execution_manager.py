import asyncio
import time
from collections.abc import Coroutine
from typing import Any

from backend.execution.execution_mode import ExecutionMode
from backend.utils.config import settings
from backend.utils.exceptions import PipelineError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionManager:
    def __init__(self, mode: ExecutionMode | None = None) -> None:
        self.mode = mode or _resolve_mode()

    async def run(
        self,
        tasks: list[tuple[str, Coroutine[Any, Any, Any]]],
    ) -> list[Any]:
        logger.info(
            "Running validation agents in %s mode",
            self.mode.value.upper(),
        )
        if self.mode == ExecutionMode.PARALLEL:
            return await self._run_parallel(tasks)
        return await self._run_sequential(tasks)

    async def _run_sequential(
        self,
        tasks: list[tuple[str, Coroutine[Any, Any, Any]]],
    ) -> list[Any]:
        results: list[Any] = []
        for name, coro in tasks:
            start = time.monotonic()
            try:
                result = await coro
            except Exception as e:
                logger.error("%s failed: %s", name, str(e))
                raise PipelineError(f"{name} failed: {e}") from e
            elapsed = time.monotonic() - start
            logger.info("%s completed in %.1fs", name, elapsed)
            results.append(result)
        return results

    async def _run_parallel(
        self,
        tasks: list[tuple[str, Coroutine[Any, Any, Any]]],
    ) -> list[Any]:
        names = [n for n, _ in tasks]
        coros = [c for _, c in tasks]
        start = time.monotonic()
        try:
            raw_results = await asyncio.gather(*coros)
        except Exception as e:
            logger.error("Parallel execution failed: %s", str(e))
            raise PipelineError(f"Parallel execution failed: {e}") from e
        elapsed_total = time.monotonic() - start
        logger.info("Parallel agents completed in %.1fs", elapsed_total)
        for name in names:
            logger.info("%s completed", name)
        return list(raw_results)


def _resolve_mode() -> ExecutionMode:
    raw = settings.execution_mode
    try:
        return ExecutionMode(raw.lower())
    except ValueError:
        logger.warning(
            "Unknown execution_mode '%s', falling back to sequential",
            raw,
        )
        return ExecutionMode.SEQUENTIAL
