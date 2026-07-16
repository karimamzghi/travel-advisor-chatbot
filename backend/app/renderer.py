from app.schemas import Itinerary


def render_itinerary_markdown(itinerary: Itinerary) -> str:
    lines: list[str] = [
        f"# {itinerary.trip_title}",
        "",
        itinerary.trip_summary,
        "",
    ]

    for day in itinerary.days:
        lines.extend(
            [
                f"## Day {day.day} — {day.title}",
                "",
            ]
        )

        for activity in day.activities:
            lines.append(
                f"### {activity.period.capitalize()}: {activity.title}"
            )
            lines.append(activity.description)

            if activity.location:
                lines.append(f"**Location:** {activity.location}")

            if activity.estimated_duration_minutes:
                lines.append(
                    "**Estimated duration:** "
                    f"{activity.estimated_duration_minutes} minutes"
                )

            if activity.estimated_cost is not None:
                currency = activity.currency or ""
                lines.append(
                    f"**Estimated cost:** "
                    f"{activity.estimated_cost:.2f} {currency}".strip()
                )

            lines.append("")

    lines.extend(
        [
            "## Practical tips",
            "",
        ]
    )

    for tip in itinerary.practical_tips:
        lines.append(f"- {tip}")

    lines.extend(
        [
            "",
            "## Estimated budget",
            "",
        ]
    )

    if itinerary.estimated_budget.total is not None:
        lines.append(
            f"**Estimated total:** "
            f"{itinerary.estimated_budget.total:.2f} "
            f"{itinerary.estimated_budget.currency}"
        )

    for note in itinerary.estimated_budget.notes:
        lines.append(f"- {note}")

    return "\n".join(lines)
