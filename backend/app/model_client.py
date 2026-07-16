from openai import OpenAI

from app.config import settings
from app.prompts import (
    ITINERARY_GENERATION_PROMPT,
    TRIP_EXTRACTION_PROMPT,
)
from app.schemas import Itinerary, TripProfile, TripUpdate


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

    def generate_itinerary(self, profile: TripProfile) -> Itinerary:
        response = self.client.responses.parse(
            model=self.model,
            instructions=ITINERARY_GENERATION_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": (
                        "Generate an itinerary for this validated trip profile:\n"
                        f"{profile.model_dump_json(indent=2)}"
                    ),
                }
            ],
            text_format=Itinerary,
        )

        return response.output_parsed
    