import json
import time
from typing import Any

from anthropic import Anthropic

from app.config import settings
from app.metrics import RequestMetrics, estimate_cost
from app.metrics_logger import print_metrics
from app.prompts import (
    ITINERARY_GENERATION_PROMPT,
    TRIP_EXTRACTION_PROMPT,
)
from app.schemas import Itinerary, TripProfile, TripUpdate
from app.tools.executor import execute_tool


ANTHROPIC_WEATHER_TOOL = {
    "name": "get_weather",
    "description": (
        "Get current weather information for a destination. "
        "Use this tool before generating the itinerary so that "
        "outdoor and indoor activities can be adapted to the "
        "weather conditions."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": (
                    "The destination city, for example Barcelona."
                ),
            }
        },
        "required": ["city"],
        "additionalProperties": False,
    },
}


class AnthropicTravelModelClient:
    def __init__(self) -> None:
        self.client = Anthropic(
            api_key=settings.anthropic_api_key,
        )
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
                        "Current trip profile:\n"
                        f"{profile.model_dump_json(indent=2)}\n\n"
                        "Recent conversation:\n"
                        f"{recent_messages}\n\n"
                        "Latest user message:\n"
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
        start_time = time.perf_counter()

        total_input_tokens = 0
        total_output_tokens = 0
        weather_tool_used = False

        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    "Generate an itinerary for this validated "
                    "trip profile:\n"
                    f"{profile.model_dump_json(indent=2)}"
                ),
            }
        ]

        # First Claude call:
        # Claude receives the profile and the weather tool.
        initial_response = self.client.messages.create(
            model=self.model,
            max_tokens=4_000,
            system=ITINERARY_GENERATION_PROMPT,
            messages=messages,
            tools=[ANTHROPIC_WEATHER_TOOL],
            tool_choice={
                "type": "auto",
            },
        )

        total_input_tokens += (
            initial_response.usage.input_tokens
        )
        total_output_tokens += (
            initial_response.usage.output_tokens
        )

        tool_uses = [
            block
            for block in initial_response.content
            if block.type == "tool_use"
        ]

        if not tool_uses:
            raise RuntimeError(
                "Anthropic did not request the weather tool."
            )

        # Claude requires its original assistant tool-use response
        # to be included in the conversation before tool results.
        messages.append(
            {
                "role": "assistant",
                "content": initial_response.content,
            }
        )

        tool_results: list[dict[str, Any]] = []

        for tool_use in tool_uses:
            print(f"\nCalling tool: {tool_use.name}")
            print(f"Arguments: {tool_use.input}")

            tool_result = execute_tool(
                tool_name=tool_use.name,
                raw_arguments=json.dumps(tool_use.input),
            )

            print(f"Result: {tool_result}\n")

            if tool_use.name == "get_weather":
                weather_tool_used = True

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

        # Second Claude call:
        # Claude receives the weather result and returns a
        # validated Itinerary.
        final_response = self.client.messages.parse(
            model=self.model,
            max_tokens=6_000,
            system=ITINERARY_GENERATION_PROMPT,
            messages=messages,
            output_format=Itinerary,
        )

        total_input_tokens += (
            final_response.usage.input_tokens
        )
        total_output_tokens += (
            final_response.usage.output_tokens
        )

        if final_response.parsed_output is None:
            raise RuntimeError(
                "Anthropic did not return a valid itinerary."
            )

        latency_seconds = (
            time.perf_counter() - start_time
        )

        metrics = RequestMetrics(
            provider="anthropic",
            model=self.model,
            latency_seconds=latency_seconds,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            estimated_cost_usd=estimate_cost(
                model=self.model,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
            ),
            weather_tool_used=weather_tool_used,
        )

        print_metrics(metrics)

        return final_response.parsed_output
