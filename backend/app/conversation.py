from dataclasses import dataclass, field

from app.schemas import Itinerary, TripProfile


@dataclass
class ConversationState:
    messages: list[dict[str, str]] = field(default_factory=list)
    trip_profile: TripProfile = field(default_factory=TripProfile)
    itinerary: Itinerary | None = None
    status: str = "collecting_information"

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def recent_messages(self, limit: int = 8) -> list[dict[str, str]]:
        return self.messages[-limit:]
