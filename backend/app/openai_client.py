import json
import time

from openai import OpenAI

from app.config import settings
from app.metrics import RequestMetrics, estimate_cost
from app.metrics_logger import print_metrics
from app.prompts import (
    ITINERARY_GENERATION_PROMPT,
    TRIP_EXTRACTION_PROMPT,
)
from app.schemas import Itinerary, TripProfile, TripUpdate
from app.tools.definitions import WEATHER_TOOL_DEFINITION
from app.tools.executor import execute_tool


class TravelModelClient:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.openai_api_key,
        )
        self.model = settings.openai_model
        self.last_metrics: RequestMetrics | None = None

    def extract_trip_update(
        self,
        *,
        profile: TripProfile,
        recent_messages: list[dict[str, str]],
        latest_message: str,
    ) -> TripUpdate:
        response = self.client.responses.parse(
            model=self.model,
            instructions=TRIP_EXTRACTION_PROMPT,
            input=[
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
            text_format=TripUpdate,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "OpenAI did not return a valid TripUpdate."
            )

        return response.output_parsed

    def generate_itinerary(
        self,
        profile: TripProfile,
    ) -> Itinerary:
        start_time = time.perf_counter()

        total_input_tokens = 0
        total_output_tokens = 0
        weather_tool_used = False

        # First model call:
        # Give the model the profile and the available weather tool.
        initial_response = self.client.responses.create(
            model=self.model,
            instructions=ITINERARY_GENERATION_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": (
                        "Generate an itinerary for this validated "
                        "trip profile:\n"
                        f"{profile.model_dump_json(indent=2)}"
                    ),
                }
            ],
            tools=[WEATHER_TOOL_DEFINITION],
        )

        if initial_response.usage is not None:
            total_input_tokens += (
                initial_response.usage.input_tokens
            )
            total_output_tokens += (
                initial_response.usage.output_tokens
            )

        function_calls = [
            item
            for item in initial_response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            raise RuntimeError(
                "OpenAI did not request the weather tool."
            )

        tool_outputs: list[dict[str, str]] = []

        for function_call in function_calls:
            print(
                f"\nCalling tool: {function_call.name}"
            )
            print(
                f"Arguments: {function_call.arguments}"
            )

            tool_result = execute_tool(
                tool_name=function_call.name,
                raw_arguments=function_call.arguments,
            )

            print(f"Result: {tool_result}\n")

            if function_call.name == "get_weather":
                weather_tool_used = True

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(tool_result),
                }
            )

        # Second model call:
        # Send the tool result back and request structured Itinerary output.
        final_response = self.client.responses.parse(
            model=self.model,
            instructions=ITINERARY_GENERATION_PROMPT,
            previous_response_id=initial_response.id,
            input=tool_outputs,
            text_format=Itinerary,
        )

        if final_response.usage is not None:
            total_input_tokens += (
                final_response.usage.input_tokens
            )
            total_output_tokens += (
                final_response.usage.output_tokens
            )

        if final_response.output_parsed is None:
            raise RuntimeError(
                "OpenAI did not return a valid itinerary."
            )

        latency_seconds = (
            time.perf_counter() - start_time
        )

        metrics = RequestMetrics(
            provider="openai",
            model=self.model,
            latency_seconds=latency_seconds,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            estimated_cost_usd=estimate_cost(
                provider="openai",
                model=self.model,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
            ),
            weather_tool_used=weather_tool_used,
        )
        self.last_metrics = metrics
        print_metrics(metrics)
        
        return final_response.output_parsed
