import pytest

from app.tools.executor import (
    ToolExecutionError,
    execute_tool,
)
def test_execute_registered_weather_tool() -> None:
    result = execute_tool(
        tool_name="get_weather",
        raw_arguments='{"city": "Barcelona"}',
    )

    assert result["city"] == "Barcelona"
    assert isinstance(result["condition"], str)
    assert result["condition"]
    assert result["temperature_c"] is not None
    assert result["source"] == "Open-Meteo"

def test_reject_unknown_tool() -> None:
    with pytest.raises(ToolExecutionError):
        execute_tool(
            tool_name="delete_everything",
            raw_arguments="{}",
        )


def test_reject_invalid_arguments() -> None:
    with pytest.raises(ToolExecutionError):
        execute_tool(
            tool_name="get_weather",
            raw_arguments='{"city": ""}',
        )


def test_reject_invalid_json() -> None:
    with pytest.raises(ToolExecutionError):
        execute_tool(
            tool_name="get_weather",
            raw_arguments="{city: Barcelona}",
        )
