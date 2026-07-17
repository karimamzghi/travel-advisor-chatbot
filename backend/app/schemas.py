from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Budget(BaseModel):
    amount: float | None = None
    currency: str | None = None
    period: Literal["total", "per_day", "unknown"] = "unknown"
    includes_accommodation: bool | None = None


class Travellers(BaseModel):
    adults: int | None = None
    children: int | None = None
    child_ages: list[int] = Field(default_factory=list)


class TripProfile(BaseModel):
    destination: str | None = None
    duration_days: int | None = None

    start_date: str | None = None
    end_date: str | None = None

    travellers: Travellers = Field(default_factory=Travellers)
    interests: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    pace: Literal[
        "relaxed",
        "balanced",
        "intensive",
        "unknown",
    ] = "unknown"

    budget: Budget = Field(default_factory=Budget)


class TripUpdate(BaseModel):
    destination: str | None = None
    duration_days: int | None = None

    start_date: str | None = None
    end_date: str | None = None

    adults: int | None = None
    children: int | None = None
    child_ages: list[int] | None = None

    interests_to_add: list[str] = Field(default_factory=list)
    interests_to_remove: list[str] = Field(default_factory=list)

    preferences_to_add: list[str] = Field(default_factory=list)
    constraints_to_add: list[str] = Field(default_factory=list)

    pace: Literal[
        "relaxed",
        "balanced",
        "intensive",
        "unknown",
    ] | None = None

    budget_amount: float | None = None
    budget_currency: str | None = None

    budget_period: Literal[
        "total",
        "per_day",
        "unknown",
    ] | None = None

    budget_includes_accommodation: bool | None = None

    explicit_correction: bool = False
    ambiguity: str | None = None
    contradiction: str | None = None


class Activity(BaseModel):
    period: Literal[
        "morning",
        "afternoon",
        "evening",
    ]

    title: str
    description: str
    location: str | None = None
    estimated_duration_minutes: int | None = None
    estimated_cost: float | None = None
    currency: str | None = None


class ItineraryDay(BaseModel):
    day: int
    title: str
    activities: list[Activity]


class EstimatedBudget(BaseModel):
    currency: str
    total: float | None = None
    notes: list[str] = Field(default_factory=list)


class Itinerary(BaseModel):
    trip_title: str
    trip_summary: str
    days: list[ItineraryDay]
    practical_tips: list[str]
    estimated_budget: EstimatedBudget


class ModelMetrics(BaseModel):
    provider: str
    model: str
    latency_seconds: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    weather_tool_used: bool


class ItineraryResult(BaseModel):
    itinerary: Itinerary
    metrics: ModelMetrics


class ChatRequest(BaseModel):
    session_id: str
    provider: Literal["openai", "anthropic"]
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    provider: str
    status: str
    assistant_message: str
    trip_profile: TripProfile
    itinerary: Itinerary | None = None
    metrics: ModelMetrics | None = None
