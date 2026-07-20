import inspect
from typing import Any, get_type_hints

from agno.tools.function import Function
from agno.utils.json_schema import get_json_schema

from backend.tools.base_tool import BaseTool


def _build_parameters(execute_method) -> dict:
    """Build a JSON schema parameters dict from a tool's execute method."""
    sig = inspect.signature(execute_method)
    param_names = [n for n in sig.parameters if n != "self"]

    type_hints: dict[str, Any] = {}
    param_descriptions: dict[str, str] = {}

    try:
        hints = get_type_hints(execute_method)
        for name in param_names:
            if name in hints and name != "return":
                type_hints[name] = hints[name]
    except Exception:
        for name in param_names:
            type_hints[name] = str

    doc = inspect.getdoc(execute_method)
    if doc:
        for name in param_names:
            param_descriptions[name] = doc

    schema = get_json_schema(type_hints=type_hints, param_descriptions=param_descriptions)
    schema["required"] = [
        name
        for name, param in sig.parameters.items()
        if name != "self" and param.default is inspect.Parameter.empty
    ]
    return schema


def adapt_tool(tool: BaseTool) -> Function:
    """Wrap a BaseTool as an Agno Function with correct parameter schema."""
    if not isinstance(tool, BaseTool):
        raise TypeError(f"Expected BaseTool instance, got {type(tool).__name__}")

    parameters = _build_parameters(tool.execute)

    async def _wrapped(**kwargs: Any) -> Any:
        result = await tool.run(**kwargs)
        if result.success:
            return result.data
        raise RuntimeError(result.error or "Tool execution failed")

    entrypoint = Function._wrap_callable(_wrapped)

    return Function(
        name=tool.name,
        description=tool.description,
        parameters=parameters,
        entrypoint=entrypoint,
        skip_entrypoint_processing=True,
    )


def adapt_tools(tools: list[BaseTool]) -> list[Function]:
    """Convert a list of BaseTool instances to Agno-compatible Functions."""
    return [adapt_tool(t) for t in tools]
