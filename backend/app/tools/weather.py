from app.tools.schemas import WeatherArguments, WeatherResult


MOCK_WEATHER_DATA: dict[str, dict[str, str | float]] = {
    "barcelona": {
        "condition": "sunny",
        "temperature_c": 25.0,
    },
    "berlin": {
        "condition": "rainy",
        "temperature_c": 16.0,
    },
    "paris": {
        "condition": "cloudy",
        "temperature_c": 19.0,
    },
    "rome": {
        "condition": "warm and sunny",
        "temperature_c": 27.0,
    },
}


def get_weather(arguments: WeatherArguments) -> WeatherResult:
    city_key = arguments.city.strip().lower()
    weather = MOCK_WEATHER_DATA.get(city_key)

    if weather is None:
        return WeatherResult(
            city=arguments.city,
            condition="unknown",
            temperature_c=None,
            source="mock",
        )
    
    return WeatherResult(
        city=arguments.city,
        condition=str(weather["condition"]),
        temperature_c=float(weather["temperature_c"]),
        source="mock",
    )
