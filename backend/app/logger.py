from app.metrics import RequestMetrics


def print_metrics(metrics: RequestMetrics) -> None:

    print("\n" + "=" * 55)

    print("LostNoMore AI Metrics")

    print("=" * 55)

    print(f"Provider            : {metrics.provider}")
    print(f"Model               : {metrics.model}")

    print()

    print(f"Latency             : {metrics.latency_seconds:.2f} sec")

    print()

    print(f"Input Tokens        : {metrics.input_tokens}")
    print(f"Output Tokens       : {metrics.output_tokens}")
    print(f"Total Tokens        : {metrics.total_tokens}")

    print()

    print(
        f"Estimated Cost      : ${metrics.estimated_cost_usd:.6f}"
    )

    print()

    print(
        f"Weather Tool Used   : {metrics.weather_tool_used}"
    )

    print("=" * 55 + "\n")
    