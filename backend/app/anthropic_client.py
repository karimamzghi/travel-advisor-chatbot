import json

from anthropic import Anthropic

from app.config import settings
from app.prompts import (
    ITINERARY_GENERATION_PROMPT,
    TRIP_EXTRACTION_PROMPT,
)
from app.schemas import Itinerary, TripProfile, TripUpdate
from app.tools.executor import execute_tool


ANTHROPIC_WEATHER_TOOL = {
    "name": "get_weather",
    "description": (
        "Retrieves current weather information for a destination city "
        "from the application's weather service. Use this before generating "
        "an itinerary so outdoor and indoor activities can be adapted to "
        "the current conditions. The tool returns the city, weather "
        "condition, temperature in Celsius, and data source."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The destination city, for example Barcelona.",
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}


class AnthropicTravelModelClient:
    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def extract_trip_update(
        self,
        *,
        profile: TripProfile,
        recent_messages: list[dict[str, str]],
        latest_message: str,
    ) -> TripUpdate:
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=2_000,
            system=TRIP_EXTRACTION_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Current trip profile:\n"
                        f"{profile.model_dump_json(indent=2)}\n\n"
                        f"Recent conversation:\n"
                        f"{recent_messages}\n\n"
                        f"Latest user message:\n"
                        f"{latest_message}"
                    ),
                }
            ],
            output_format=TripUpdate,
        )

        if response.parsed_output is None:
            raise RuntimeError(
                "Anthropic did not return a valid TripUpdate."
            )

        return response.parsed_output

    def generate_itinerary(
        self,
        profile: TripProfile,
    ) -> Itinerary:
        user_message = (
            "Generate an itinerary for this validated trip profile:\n"
            f"{profile.model_dump_json(indent=2)}"
        )

        messages: list[dict] = [
            {
                "role": "user",
                "content": user_message,
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4_000,
            system=ITINERARY_GENERATION_PROMPT,
            messages=messages,
            tools=[ANTHROPIC_WEATHER_TOOL],
            tool_choice={"type": "auto"},
        )

        tool_uses = [
            block
            for block in response.content
            if block.type == "tool_use"
        ]

        if not tool_uses:
            raise RuntimeError(
                "Anthropic did not request the weather tool."
            )

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_results = []

        for tool_use in tool_uses:
            print(f"\n🔧 Calling tool: {tool_use.name}")
            print(f"Arguments: {tool_use.input}")

            tool_result = execute_tool(
                tool_name=tool_use.name,
                raw_arguments=json.dumps(tool_use.input),
            )

            print(f"Result: {tool_result}\n")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(tool_result),
                }
            )

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

        final_response = self.client.messages.parse(
            model=self.model,
            max_tokens=6_000,
            system=ITINERARY_GENERATION_PROMPT,
            messages=messages,
            output_format=Itinerary,
        )

        if final_response.parsed_output is None:
            raise RuntimeError(
                "Anthropic did not return a valid itinerary."
            )

        return final_response.parsed_output
