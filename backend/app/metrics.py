from dataclasses import dataclass


@dataclass
class RequestMetrics:
    provider: str
    model: str
    latency_seconds: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    weather_tool_used: bool


OPENAI_PRICING = {
    "gpt-5-nano": {
        "input": 0.05,
        "output": 0.40,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "output": 2.00,
    },
}


ANTHROPIC_PRICING = {
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
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
        pricing = OPENAI_PRICING.get(model)

    elif provider == "anthropic":
        pricing = ANTHROPIC_PRICING.get(model)

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

    return round(input_cost + output_cost, 6)
