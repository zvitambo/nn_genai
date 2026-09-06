from enum import StrEnum
from pydantic import BaseModel, Field, model_validator

from nn_genai.models.research_status import ResearchStatus




class EvidenceCitationDraft(BaseModel):
    evidence_id: str = Field(
        min_length=21,
        pattern=r"^evidence-[0-9a-f]{12}$",
        description=(
            "Exact Evidence ID returned by search_web. "
            "It must not be a URL, title, or invented identifier."
        ),
    )
    supporting_claim: str = Field(
        min_length=1,
        description=(
            "A claim supported by the snippet associated with this "
            "evidence ID."
        ),
    )

class ResearchDraft(BaseModel):
    person_name: str
    selected_work: str
    status: ResearchStatus
    reasoning: str
    citations: list[EvidenceCitationDraft]
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def require_citations(self) -> "ResearchDraft":
        if not self.citations:
            raise ValueError(
                "A research conclusion requires retrieved evidence."
            )
        return self
