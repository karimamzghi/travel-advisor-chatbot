from dataclasses import dataclass


@dataclass
class RequestMetrics:
    provider: str
    model: str
    latency_seconds: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    weather_tool_used: bool

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


MODEL_PRICING_PER_MILLION = {
    "gpt-5-nano": {
        "input": 0.05,
        "output": 0.40,
    },
    "claude-sonnet-5": {
        "input": 3.00,
        "output": 15.00,
    },
}


def estimate_cost(
    *,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    if provider == "openai":
        pricing = MODEL_PRICING_PER_MILLION.get(model)
    elif provider == "anthropic":
        pricing = MODEL_PRICING_PER_MILLION.get(model)
    else:
        return 0.0

    if pricing is None:
        return 0.0

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output"]

    return input_cost + output_cost
