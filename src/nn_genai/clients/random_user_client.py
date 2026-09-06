from datetime import datetime

import httpx
from typing import Protocol

from nn_genai.models.person import Person



class RandomUserApiClient:
    BASE_URL = "https://randomuser.me/api/"

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout

    async def fetch_users(self, count: int) -> list[Person]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                self.BASE_URL,
                params={"results": count},
            )
            response.raise_for_status()

            payload = response.json()

        results = payload.get("results")

        if not isinstance(results, list):
            raise ValueError(
                "RandomUser API returned an invalid results payload")

        return [
            self._to_person(user)
            for user in results
        ]

    @staticmethod
    def _to_person(user: dict) -> Person:
        name = user["name"]
        dob = user["dob"]
        location = user.get("location", {})

        date_of_birth = datetime.fromisoformat(
            dob["date"].replace("Z", "+00:00")
        ).date()

        return Person(
            first_name=name["first"],
            last_name=name["last"],
            date_of_birth=date_of_birth,
            nationality=user.get("nat"),
            country=location.get("country"),
            city=location.get("city"),
        )
