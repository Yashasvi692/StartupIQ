from typing import Any

from backend.tools.base_tool import BaseTool


def adapt_tool(tool: BaseTool) -> Any:
    """Wrap a BaseTool as an Agno-compatible async callable.

    The returned callable preserves the tool's name and description
    so Agno can expose them to the LLM.
    """
    if not isinstance(tool, BaseTool):
        raise TypeError(f"Expected BaseTool instance, got {type(tool).__name__}")

    async def _wrapped(**kwargs: Any) -> Any:
        result = await tool.run(**kwargs)
        if result.success:
            return result.data
        raise RuntimeError(result.error or "Tool execution failed")

    _wrapped.__name__ = tool.name
    _wrapped.__doc__ = tool.description
    return _wrapped


def adapt_tools(tools: list[BaseTool]) -> list[Any]:
    """Convert a list of BaseTool instances to Agno-compatible callables."""
    return [adapt_tool(t) for t in tools]
