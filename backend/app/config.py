import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.travel_model = os.getenv("TRAVEL_MODEL")

        if not self.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        if not self.travel_model:
            raise RuntimeError("TRAVEL_MODEL is not configured.")

settings = Settings()
