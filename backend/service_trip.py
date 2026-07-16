from app.schemas import TripProfile


def get_missing_required_fields(profile: TripProfile) -> list[str]:
    missing: list[str] = []

    if not profile.destination:
        missing.append("destination")

    if profile.duration_days is None:
        missing.append("duration_days")

    if not profile.interests:
        missing.append("interests")

    return missing
