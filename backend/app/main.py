from openai import APIConnectionError, APIError, RateLimitError

from app.conversation import ConversationState
from app.model_client import TravelModelClient
from app.renderer import render_itinerary_markdown
from app.trip_service import (
    apply_trip_update,
    choose_next_question,
    get_missing_required_fields,
)


def run_chatbot() -> None:
    client = TravelModelClient()
    state = ConversationState()

    greeting = (
        "Hello! I’m your AI Travel Advisor. My name is LostNoMore :D "
        "I’ll help you create a personalized itinerary. "
        "Where would you like to travel?"
    )

    print(f"\nAssistant: {greeting}\n")
    state.add_message("assistant", greeting)

    while True:
        user_message = input("You: ").strip()

        if not user_message:
            print("Assistant: Please enter a message.")
            continue

        if user_message.lower() in {"quit", "exit"}:
            print("Assistant: Goodbye!")
            break

        state.add_message("user", user_message)

        try:
            update = client.extract_trip_update(
                profile=state.trip_profile,
                recent_messages=state.recent_messages(),
                latest_message=user_message,
            )

            if update.ambiguity:
                response = update.ambiguity
                state.add_message("assistant", response)
                print(f"\nAssistant: {response}\n")
                continue

            if update.contradiction and not update.explicit_correction:
                response = update.contradiction
                state.add_message("assistant", response)
                print(f"\nAssistant: {response}\n")
                continue

            state.trip_profile = apply_trip_update(
                state.trip_profile,
                update,
            )

            missing_fields = get_missing_required_fields(
                state.trip_profile
            )

            if missing_fields:
                response = choose_next_question(missing_fields)
                state.add_message("assistant", response)
                print(f"\nAssistant: {response}\n")
                continue

            state.status = "generating_itinerary"
            itinerary = client.generate_itinerary(state.trip_profile)

            state.itinerary = itinerary
            state.status = "completed"

            markdown = render_itinerary_markdown(itinerary)
            state.add_message("assistant", markdown)

            print(f"\nAssistant:\n\n{markdown}\n")
            break

        except RateLimitError:
            print(
                "\nAssistant: The model provider is currently rate-limiting "
                "requests. Please wait and try again.\n"
            )
        except APIConnectionError:
            print(
                "\nAssistant: I could not connect to the model provider. "
                "Please check your internet connection.\n"
            )
        except APIError as exc:
            print(
                "\nAssistant: The model provider returned an error. "
                f"Details: {exc}\n"
            )
        except Exception as exc:
            print(
                "\nAssistant: An unexpected error occurred. "
                f"Details: {exc}\n"
            )


if __name__ == "__main__":
    run_chatbot()