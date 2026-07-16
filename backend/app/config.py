import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


ProviderName = Literal["openai", "anthropic"]


class Settings:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5-nano",
        )

        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv(
            "ANTHROPIC_MODEL",
            "claude-sonnet-4-6",
        )

        self.default_provider: ProviderName = self._read_provider(
            os.getenv("DEFAULT_PROVIDER", "openai")
        )

        if not self.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        if not self.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not configured."
            )

    @staticmethod
    def _read_provider(value: str) -> ProviderName:
        normalized = value.strip().lower()

        if normalized not in {"openai", "anthropic"}:
            raise RuntimeError(
                "DEFAULT_PROVIDER must be 'openai' or 'anthropic'."
            )

        return normalized  # type: ignore[return-value]


settings = Settings()
