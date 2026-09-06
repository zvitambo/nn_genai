from google import genai

from nn_genai.infrastructure.llm.prompts import (
    SYSTEM_PROMPT,
    build_identity_prompt,
)
from nn_genai.models.person import Person
from nn_genai.models.person_identity import PersonIdentity


class GeminiLLMProvider:
    """Gemini implementation of the LLMProvider port."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.6-flash",
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def identify_person(
        self,
        person: Person,
    ) -> PersonIdentity:
        prompt = build_identity_prompt(
            name=person.full_name,
            nationality=person.nationality,
            country=person.country,
            city=person.city,
        )

        interaction = await self._client.aio.interactions.create(
            model=self._model,
            input=prompt,
            system_instruction=SYSTEM_PROMPT,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": PersonIdentity.model_json_schema(),
            },
        )

        if not interaction.output_text:
            raise ValueError("Gemini returned an empty response")

        return PersonIdentity.model_validate_json(
            interaction.output_text
        )
