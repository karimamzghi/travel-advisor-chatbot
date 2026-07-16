from app.schemas import TripProfile, TripUpdate
from app.trip_service import (
    apply_trip_update,
    get_missing_required_fields,
)


def test_empty_profile_has_all_required_fields_missing() -> None:
    profile = TripProfile()

    assert get_missing_required_fields(profile) == [
        "destination",
        "duration_days",
        "interests",
        "travellers",
        "budget",
        "pace",
    ]


def test_profile_with_only_original_fields_is_not_ready() -> None:
    profile = TripProfile(
        destination="Barcelona",
        duration_days=4,
        interests=["food"],
    )

    assert get_missing_required_fields(profile) == [
        "travellers",
        "budget",
        "pace",
    ]


def test_complete_profile_is_ready() -> None:
    profile = TripProfile(
        destination="Barcelona",
        duration_days=4,
        interests=["food"],
        pace="balanced",
    )

    profile.travellers.adults = 1
    profile.travellers.children = 0

    profile.budget.amount = 200
    profile.budget.currency = "EUR"
    profile.budget.period = "per_day"
    profile.budget.includes_accommodation = False

    assert get_missing_required_fields(profile) == []


def test_apply_update_changes_duration() -> None:
    profile = TripProfile(
        destination="Barcelona",
        duration_days=3,
        interests=["food"],
    )

    update = TripUpdate(
        duration_days=5,
        explicit_correction=True,
    )

    updated = apply_trip_update(profile, update)

    assert updated.duration_days == 5


def test_apply_update_removes_interest() -> None:
    profile = TripProfile(
        destination="Barcelona",
        duration_days=4,
        interests=["food", "museums"],
    )

    update = TripUpdate(
        interests_to_remove=["museums"],
        explicit_correction=True,
    )

    updated = apply_trip_update(profile, update)

    assert updated.interests == ["food"]


def test_apply_update_adds_travellers_budget_and_pace() -> None:
    profile = TripProfile(
        destination="Barcelona",
        duration_days=5,
        interests=["sports", "shopping"],
    )

    update = TripUpdate(
        adults=2,
        children=1,
        child_ages=[6],
        pace="relaxed",
        budget_amount=250,
        budget_currency="EUR",
        budget_period="per_day",
        budget_includes_accommodation=False,
    )

    updated = apply_trip_update(profile, update)

    assert updated.travellers.adults == 2
    assert updated.travellers.children == 1
    assert updated.travellers.child_ages == [6]

    assert updated.pace == "relaxed"

    assert updated.budget.amount == 250
    assert updated.budget.currency == "EUR"
    assert updated.budget.period == "per_day"
    assert updated.budget.includes_accommodation is False


def test_profile_with_travellers_but_without_budget_and_pace_is_not_ready() -> None:
    profile = TripProfile(
        destination="Rome",
        duration_days=3,
        interests=["food", "history"],
    )

    profile.travellers.adults = 2
    profile.travellers.children = 0

    assert get_missing_required_fields(profile) == [
        "budget",
        "pace",
    ]
