from openai import OpenAI
import json

from app.config import settings
from app.prompts import (
    ITINERARY_GENERATION_PROMPT,
    TRIP_EXTRACTION_PROMPT,
)
from app.schemas import Itinerary, TripProfile, TripUpdate
from app.tools.definitions import WEATHER_TOOL_DEFINITION
from app.tools.executor import execute_tool


class TravelModelClient:
    
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.travel_model

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
                        f"Current trip profile:\n"
                        f"{profile.model_dump_json(indent=2)}\n\n"
                        f"Recent conversation:\n"
                        f"{recent_messages}\n\n"
                        f"Latest user message:\n"
                        f"{latest_message}"
                    ),
                }
            ],
            text_format=TripUpdate,
        )

        return response.output_parsed
    
    def generate_itinerary(
        self,
        profile: TripProfile,
    ) -> Itinerary:

        # First request
        response = self.client.responses.create(
            model=self.model,
            instructions=ITINERARY_GENERATION_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": (
                        "Generate an itinerary for this trip profile:\n"
                        f"{profile.model_dump_json(indent=2)}"
                    ),
                }
            ],
            tools=[WEATHER_TOOL_DEFINITION],
        )

        # Continue until the model is done
        while True:

            function_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            # No tool requested -> we're finished
            if not function_calls:

                final = self.client.responses.parse(
                    model=self.model,
                    instructions=ITINERARY_GENERATION_PROMPT,
                    previous_response_id=response.id,
                    text_format=Itinerary,
                )

                if final.output_parsed is None:
                    raise RuntimeError(
                        "Failed to parse itinerary."
                    )

                return final.output_parsed

            tool_outputs = []

            for function_call in function_calls:

                print(f"\n🔧 Calling tool: {function_call.name}")
                print(f"Arguments: {function_call.arguments}")

                tool_result = execute_tool(
                    tool_name=function_call.name,
                    raw_arguments=function_call.arguments,
                )

                print(f"Result: {tool_result}\n")

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": function_call.call_id,
                        "output": json.dumps(tool_result),
                    }
                )

            response = self.client.responses.create(
                model=self.model,
                instructions=ITINERARY_GENERATION_PROMPT,
                previous_response_id=response.id,
                input=tool_outputs,
            )

