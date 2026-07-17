from anthropic import (
    APIConnectionError as AnthropicConnectionError,
)
from anthropic import APIError as AnthropicAPIError
from anthropic import RateLimitError as AnthropicRateLimitError
from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIError, RateLimitError
from fastapi.middleware.cors import CORSMiddleware

from app.provider_factory import create_travel_client
from app.renderer import render_itinerary_markdown
from app.schemas import ChatRequest, ChatResponse
from app.session_store import session_store
from app.trip_service import (
    apply_trip_update,
    choose_next_question,
    get_missing_required_fields,
)


app = FastAPI(
    title="LostNoMore API",
    description="AI-powered conversational travel-planning API.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://travel.zeynlo.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "LostNoMore API",
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest) -> ChatResponse:
    state = session_store.get_or_create(
        request.session_id
    )

    client = create_travel_client(
        request.provider
    )

    state.add_message(
        "user",
        request.message,
    )

    try:
        update = client.extract_trip_update(
            profile=state.trip_profile,
            recent_messages=state.recent_messages(),
            latest_message=request.message,
        )

        if update.ambiguity:
            assistant_message = update.ambiguity

            state.add_message(
                "assistant",
                assistant_message,
            )

            return ChatResponse(
                session_id=request.session_id,
                provider=request.provider,
                status="needs_clarification",
                assistant_message=assistant_message,
                trip_profile=state.trip_profile,
                itinerary=None,
            )

        if (
            update.contradiction
            and not update.explicit_correction
        ):
            assistant_message = update.contradiction

            state.add_message(
                "assistant",
                assistant_message,
            )

            return ChatResponse(
                session_id=request.session_id,
                provider=request.provider,
                status="needs_clarification",
                assistant_message=assistant_message,
                trip_profile=state.trip_profile,
                itinerary=None,
            )

        state.trip_profile = apply_trip_update(
            state.trip_profile,
            update,
        )

        missing_fields = get_missing_required_fields(
            state.trip_profile
        )

        if missing_fields:
            assistant_message = choose_next_question(
                missing_fields
            )

            state.status = "collecting_information"

            state.add_message(
                "assistant",
                assistant_message,
            )

            return ChatResponse(
                session_id=request.session_id,
                provider=request.provider,
                status="collecting_information",
                assistant_message=assistant_message,
                trip_profile=state.trip_profile,
                itinerary=None,
            )

        state.status = "generating_itinerary"

        itinerary = client.generate_itinerary(
            state.trip_profile
        )

        request_metrics = getattr(
            client,
            "last_metrics",
            None,
        )

        metrics_response = None

        if request_metrics is not None:
            metrics_response = {
                "provider": request_metrics.provider,
                "model": request_metrics.model,
                "latency_seconds": request_metrics.latency_seconds,
                "input_tokens": request_metrics.input_tokens,
                "output_tokens": request_metrics.output_tokens,
                "total_tokens": request_metrics.total_tokens,
                "estimated_cost_usd": (
                    request_metrics.estimated_cost_usd
                ),
                "weather_tool_used": (
                    request_metrics.weather_tool_used
                ),
            }

        state.itinerary = itinerary
        state.status = "completed"

        assistant_message = (
            render_itinerary_markdown(itinerary)
        )

        state.add_message(
            "assistant",
            assistant_message,
        )

        return ChatResponse(
            session_id=request.session_id,
            provider=request.provider,
            status="completed",
            assistant_message=assistant_message,
            trip_profile=state.trip_profile,
            itinerary=itinerary,
            metrics=metrics_response,
        )

    except (
        RateLimitError,
        AnthropicRateLimitError,
    ) as exc:
        raise HTTPException(
            status_code=429,
            detail="The selected provider is rate-limiting requests.",
        ) from exc

    except (
        APIConnectionError,
        AnthropicConnectionError,
    ) as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to the selected model provider.",
        ) from exc

    except (
        APIError,
        AnthropicAPIError,
    ) as exc:
        provider_status = getattr(
            exc,
            "status_code",
            None,
        )

        status_code = (
            503
            if provider_status
            and provider_status >= 500
            else 502
        )

        raise HTTPException(
            status_code=status_code,
            detail=(
                "The selected model provider returned an error."
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.delete(
    "/sessions/{session_id}",
)
def delete_session(
    session_id: str,
) -> dict[str, str]:
    deleted = session_store.delete(session_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    return {
        "status": "deleted",
        "session_id": session_id,
    }
