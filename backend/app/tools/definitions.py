WEATHER_TOOL_DEFINITION = {
    "type": "function",
    "name": "get_weather",
    "description": (
        "Get weather information for a destination city. "
        "Use this tool when weather may affect the itinerary."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The destination city.",
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}
