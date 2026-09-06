import asyncio

from nn_genai.clients.random_user_client import RandomUserApiClient
from nn_genai.services.person_service import PersonService


async def main() -> None:
    client = RandomUserApiClient()
    person_service = PersonService()

    people = await client.fetch_users(20)

    print(f"Fetched {len(people)} people")

    eligible_people = person_service.filter_people(people)

    names = person_service.format_people(eligible_people)

    print(names)


if __name__ == "__main__":
    asyncio.run(main())
