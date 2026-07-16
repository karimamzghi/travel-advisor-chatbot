from app.metrics import RequestMetrics

def print_metrics(metrics: RequestMetrics) -> None:
    print("\n" + "=" * 55)
    print("LostNoMore — Model Metrics")
    print("=" * 55)

    print(f"Provider           : {metrics.provider}")
    print(f"Model              : {metrics.model}")
    print(f"Latency            : {metrics.latency_seconds:.2f} seconds")
    print(f"Input tokens       : {metrics.input_tokens}")
    print(f"Output tokens      : {metrics.output_tokens}")
    print(f"Total tokens       : {metrics.total_tokens}")
    print(f"Estimated cost     : ${metrics.estimated_cost_usd:.6f}")
    print(f"Weather tool used  : {metrics.weather_tool_used}")

    print("=" * 55 + "\n")