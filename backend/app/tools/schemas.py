from pydantic import BaseModel, Field


class WeatherArguments(BaseModel):
    city: str = Field(
        min_length=1,
        description="The city for which weather information is requested.",
    )


class WeatherResult(BaseModel):
    city: str
    condition: str
    temperature_c: float | None = None
    source: str = "mock"
