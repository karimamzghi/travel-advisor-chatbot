import json
from typing import Any

from pydantic import ValidationError

from app.tools.registry import (
    TOOL_ARGUMENT_SCHEMAS,
    TOOL_REGISTRY,
)


class ToolExecutionError(RuntimeError):
    pass


def execute_tool(
    *,
    tool_name: str,
    raw_arguments: str,
) -> dict[str, Any]:
    if tool_name not in TOOL_REGISTRY:
        raise ToolExecutionError(
            f"Tool '{tool_name}' is not registered."
        )

    if tool_name not in TOOL_ARGUMENT_SCHEMAS:
        raise ToolExecutionError(
            f"No argument schema registered for '{tool_name}'."
        )

    try:
        parsed_arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ToolExecutionError(
            f"Tool arguments are not valid JSON: {exc}"
        ) from exc

    schema = TOOL_ARGUMENT_SCHEMAS[tool_name]

    try:
        validated_arguments = schema.model_validate(
            parsed_arguments
        )
    except ValidationError as exc:
        raise ToolExecutionError(
            f"Invalid arguments for tool '{tool_name}': {exc}"
        ) from exc

    tool_function = TOOL_REGISTRY[tool_name]

    result = tool_function(validated_arguments)

    if hasattr(result, "model_dump"):
        return result.model_dump()

    if isinstance(result, dict):
        return result

    raise ToolExecutionError(
        f"Tool '{tool_name}' returned an unsupported result."
    )
