from typing import Protocol

from app.anthropic_client import AnthropicTravelModelClient
from app.config import ProviderName
from app.openai_client import TravelModelClient
from app.schemas import Itinerary, TripProfile, TripUpdate


class TravelClientProtocol(Protocol):
    def extract_trip_update(
        self,
        *,
        profile: TripProfile,
        recent_messages: list[dict[str, str]],
        latest_message: str,
    ) -> TripUpdate:
        ...

    def generate_itinerary(
        self,
        profile: TripProfile,
    ) -> Itinerary:
        ...


def create_travel_client(
    provider: ProviderName,
) -> TravelClientProtocol:
    if provider == "openai":
        return TravelModelClient()

    if provider == "anthropic":
        return AnthropicTravelModelClient()

    raise ValueError(f"Unsupported provider: {provider}")
