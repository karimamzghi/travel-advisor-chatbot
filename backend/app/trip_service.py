from app.schemas import TripProfile


def get_missing_required_fields(profile: TripProfile) -> list[str]:
    missing: list[str] = []

    if not profile.destination:
        missing.append("destination")

    if profile.duration_days is None:
        missing.append("duration_days")

    if not profile.interests:
        missing.append("interests")
    
    travellers_known = (
        profile.travellers.adults is not None
        or profile.travellers.children is not None
    )

    if not travellers_known:
        missing.append("travellers")

    if profile.budget.amount is None:
        missing.append("budget")

    if profile.pace == "unknown":
        missing.append("pace")

    return missing

from app.schemas import TripProfile, TripUpdate


def merge_unique(existing: list[str], additions: list[str]) -> list[str]:
    normalized = {item.strip().lower(): item.strip() for item in existing}

    for item in additions:
        clean_item = item.strip()
        if clean_item:
            normalized[clean_item.lower()] = clean_item

    return list(normalized.values())


def remove_items(existing: list[str], removals: list[str]) -> list[str]:
    removal_set = {item.strip().lower() for item in removals}

    return [
        item
        for item in existing
        if item.strip().lower() not in removal_set
    ]


def apply_trip_update(
    profile: TripProfile,
    update: TripUpdate,
) -> TripProfile:
    updated = profile.model_copy(deep=True)

    if update.destination is not None:
        updated.destination = update.destination

    if update.duration_days is not None:
        updated.duration_days = update.duration_days

    if update.start_date is not None:
        updated.start_date = update.start_date

    if update.end_date is not None:
        updated.end_date = update.end_date

    if update.adults is not None:
        updated.travellers.adults = update.adults

    if update.children is not None:
        updated.travellers.children = update.children

    if update.child_ages is not None:
        updated.travellers.child_ages = update.child_ages

    updated.interests = merge_unique(
        updated.interests,
        update.interests_to_add,
    )

    updated.interests = remove_items(
        updated.interests,
        update.interests_to_remove,
    )

    updated.preferences = merge_unique(
        updated.preferences,
        update.preferences_to_add,
    )

    updated.constraints = merge_unique(
        updated.constraints,
        update.constraints_to_add,
    )

    if update.pace is not None:
        updated.pace = update.pace

    if update.budget_amount is not None:
        updated.budget.amount = update.budget_amount

    if update.budget_currency is not None:
        updated.budget.currency = update.budget_currency

    if update.budget_period is not None:
        updated.budget.period = update.budget_period

    if update.budget_includes_accommodation is not None:
        updated.budget.includes_accommodation = (
            update.budget_includes_accommodation
        )

    return updated

QUESTION_BY_FIELD = {
    "destination": "Where would you like to travel?",
    "duration_days": "How many days would you like the itinerary to cover?",
    "interests": (
        "What kinds of activities interest you most for example food, "
        "museums, nature, beaches, shopping, or nightlife?"
    ),
     "travellers": (
        "Who will be travelling? Solo with others? Please include the number of adults, "
        "the number of children, and the children's ages if applicable."
    ),
    "budget": (
        "What approximate budget should I plan around? "
        "Please mention whether it is per day or for the whole trip, "
        "and whether accommodation is included."
    ),
    "pace": (
        "What travel pace would you prefer: relaxed, balanced, or intensive?"
    ),
}

def choose_next_question(missing_fields: list[str]) -> str:
    if not missing_fields:
        raise ValueError("No required fields are missing.")

    return QUESTION_BY_FIELD[missing_fields[0]]
