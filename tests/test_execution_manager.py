import asyncio
import warnings
from unittest.mock import patch

import pytest

from backend.execution.execution_manager import ExecutionManager
from backend.execution.execution_mode import ExecutionMode
from backend.utils.exceptions import PipelineError


class TestExecutionMode:
    def test_sequential_enum_value(self):
        assert ExecutionMode.SEQUENTIAL.value == "sequential"

    def test_parallel_enum_value(self):
        assert ExecutionMode.PARALLEL.value == "parallel"

    def test_enum_members(self):
        assert set(ExecutionMode.__members__) == {"SEQUENTIAL", "PARALLEL"}


class TestExecutionManagerSequential:
    @pytest.mark.asyncio
    async def test_executes_in_order(self):
        order: list[str] = []

        async def task_a():
            order.append("a")
            return "A"

        async def task_b():
            order.append("b")
            return "B"

        async def task_c():
            order.append("c")
            return "C"

        mgr = ExecutionManager(mode=ExecutionMode.SEQUENTIAL)
        results = await mgr.run(
            [
                ("a", task_a()),
                ("b", task_b()),
                ("c", task_c()),
            ]
        )

        assert order == ["a", "b", "c"]
        assert results == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_preserves_result_ordering(self):
        async def fn(val: str):
            await asyncio.sleep(0)
            return val

        mgr = ExecutionManager(ExecutionMode.SEQUENTIAL)
        results = await mgr.run(
            [
                ("first", fn("1")),
                ("second", fn("2")),
                ("third", fn("3")),
            ]
        )
        assert results == ["1", "2", "3"]

    @pytest.mark.asyncio
    async def test_stops_on_first_failure(self):
        call_count = 0

        async def good():
            nonlocal call_count
            call_count += 1
            return "ok"

        async def bad():
            nonlocal call_count
            call_count += 1
            raise ValueError("boom")

        async def never_reached():
            nonlocal call_count
            call_count += 1
            return "should_not_reach"

        never_coro = never_reached()

        mgr = ExecutionManager(ExecutionMode.SEQUENTIAL)
        with pytest.raises(PipelineError, match="bad failed"):
            await mgr.run(
                [
                    ("good", good()),
                    ("bad", bad()),
                    ("never", never_coro),
                ]
            )

        assert call_count == 2, "Third task should not have been executed"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            never_coro.close()

    @pytest.mark.asyncio
    async def test_defaults_to_sequential(self):
        mgr = ExecutionManager()
        assert mgr.mode == ExecutionMode.SEQUENTIAL

    @pytest.mark.asyncio
    async def test_default_mode_from_settings(self):
        with patch(
            "backend.execution.execution_manager.settings.execution_mode",
            "sequential",
        ):
            mgr = ExecutionManager()
            assert mgr.mode == ExecutionMode.SEQUENTIAL


class TestExecutionManagerParallel:
    @pytest.mark.asyncio
    async def test_executes_concurrently(self):
        started = 0
        finished = 0

        async def track():
            nonlocal started, finished
            started += 1
            await asyncio.sleep(0.05)
            finished += 1
            return "done"

        async def track2():
            nonlocal started, finished
            started += 1
            await asyncio.sleep(0.01)
            finished += 1
            return "done2"

        mgr = ExecutionManager(mode=ExecutionMode.PARALLEL)
        results = await mgr.run(
            [
                ("slow", track()),
                ("fast", track2()),
            ]
        )

        assert started == 2
        assert finished == 2
        assert results == ["done", "done2"]

    @pytest.mark.asyncio
    async def test_preserves_result_ordering(self):
        async def slow():
            await asyncio.sleep(0.05)
            return "slow_result"

        async def fast():
            await asyncio.sleep(0.01)
            return "fast_result"

        mgr = ExecutionManager(ExecutionMode.PARALLEL)
        results = await mgr.run(
            [
                ("slow", slow()),
                ("fast", fast()),
            ]
        )
        assert results == ["slow_result", "fast_result"]

    @pytest.mark.asyncio
    async def test_exception_propagation(self):
        async def ok():
            return "ok"

        async def fail():
            raise ValueError("explosion")

        mgr = ExecutionManager(ExecutionMode.PARALLEL)
        with pytest.raises(PipelineError, match="explosion"):
            await mgr.run(
                [
                    ("ok", ok()),
                    ("fail", fail()),
                ]
            )


class TestExecutionManagerErrorHandling:
    @pytest.mark.asyncio
    async def test_custom_exception_raised_as_pipeline_error(self):
        class CustomError(Exception):
            pass

        async def crash():
            raise CustomError("custom crash")

        mgr = ExecutionManager(ExecutionMode.SEQUENTIAL)
        with pytest.raises(PipelineError, match="custom crash"):
            await mgr.run(
                [
                    ("crash", crash()),
                ]
            )

    @pytest.mark.asyncio
    async def test_parallel_exception_raised_as_pipeline_error(self):
        async def crash():
            raise RuntimeError("parallel crash")

        mgr = ExecutionManager(ExecutionMode.PARALLEL)
        with pytest.raises(PipelineError, match="parallel crash"):
            await mgr.run(
                [
                    ("crash", crash()),
                ]
            )
