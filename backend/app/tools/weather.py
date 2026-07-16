import requests

from app.tools.schemas import (
    WeatherArguments,
    WeatherResult,
)

GEOCODING_API = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_API = (
    "https://api.open-meteo.com/v1/forecast"
)

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Snow",
    80: "Rain showers",
    95: "Thunderstorm",
}


def get_weather(
    arguments: WeatherArguments,
) -> WeatherResult:

    city = arguments.city.strip()

    geo_response = requests.get(
        GEOCODING_API,
        params={
            "name": city,
            "count": 1,
        },
        timeout=10,
    )

    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return WeatherResult(
            city=city,
            condition="Unknown",
            temperature_c=None,
            source="Open-Meteo",
        )

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    weather_response = requests.get(
        WEATHER_API,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
        },
        timeout=10,
    )

    weather_data = weather_response.json()

    if "current" not in weather_data:
        return WeatherResult(
            city=city,
            condition="Unknown",
            temperature_c=None,
            source="Open-Meteo",
        )

    weather = weather_data["current"]

    return WeatherResult(
        city=city,
        condition=WEATHER_CODES.get(
            weather["weather_code"],
            "Unknown",
        ),
        temperature_c=weather["temperature_2m"],
        source="Open-Meteo",
    )
