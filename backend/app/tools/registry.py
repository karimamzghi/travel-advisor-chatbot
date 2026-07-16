from collections.abc import Callable
from typing import Any

from app.tools.schemas import WeatherArguments
from app.tools.weather import get_weather


ToolFunction = Callable[[Any], Any]


TOOL_REGISTRY: dict[str, ToolFunction] = {
    "get_weather": get_weather,
}


TOOL_ARGUMENT_SCHEMAS = {
    "get_weather": WeatherArguments,
}
