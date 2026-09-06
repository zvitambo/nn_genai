# src/nn_genai/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    gemini_api_key: str
    gemini_model: str
    goggle_api_key: str
    tavily_api_key: str

    def __init__(self) -> None:
        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY",
            "",
        )
        self.gemini_model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )
        self.google_api_key = os.getenv(
                    " GOOGLE_API_KEY",
                    "",
                )
        self.tavily_api_key = os.getenv(
            "TAVILY_API_KEY",
            "",
        )
       

settings = Settings()
