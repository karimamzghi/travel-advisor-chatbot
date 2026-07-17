from app.tools.schemas import WeatherArguments
from app.tools.weather import get_weather


def test_get_weather_for_known_city() -> None:
    arguments = WeatherArguments(city="Barcelona")

    result = get_weather(arguments)

    assert result.city == "Barcelona"
    assert result.condition == "sunny"
    assert result.temperature_c == 25.0
    assert result.source == "mock"


def test_get_weather_is_case_insensitive() -> None:
    arguments = WeatherArguments(city="BARCELONA")

    result = get_weather(arguments)

    assert result.condition == "sunny"


def test_get_weather_for_unknown_city() -> None:
    arguments = WeatherArguments(city="Unknown City")

    result = get_weather(arguments)

    assert result.condition == "unknown"
    assert result.temperature_c is None
from app.tools.schemas import WeatherArguments
from app.tools.weather import get_weather


def test_get_weather_for_known_city() -> None:
    arguments = WeatherArguments(city="Barcelona")

    result = get_weather(arguments)

    assert result.city == "Barcelona"
    assert isinstance(result.condition, str)
    assert result.condition
    assert result.temperature_c is not None
    assert result.source == "Open-Meteo"


def test_get_weather_is_case_insensitive() -> None:
    arguments = WeatherArguments(city="BARCELONA")

    result = get_weather(arguments)

    assert result.city == "BARCELONA"
    assert isinstance(result.condition, str)
    assert result.condition
    assert result.temperature_c is not None
    assert result.source == "Open-Meteo"


def test_get_weather_for_unknown_city() -> None:
    arguments = WeatherArguments(city="Unknown City")

    result = get_weather(arguments)

    assert result.city == "Unknown City"
    assert result.condition == "Unknown"
    assert result.temperature_c is None
    assert result.source == "Open-Meteo"
    