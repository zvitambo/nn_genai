import pytest

from nn_genai.application.research.provenance_validator import (
    ProvenanceValidator,
)
from nn_genai.infrastructure.agents.langchain_research_agent import (
    LangChainResearchAgent,
)
from nn_genai.models.search_result import SearchResult

from tests.fakes.fake_research_model import FakeResearchModel
from tests.fakes.fake_search_provider import FakeSearchProvider

import pytest

from nn_genai.application.research.provenance_validator import (
    InvalidEvidenceReferenceError,
    ProvenanceValidator,
)


@pytest.mark.asyncio
async def test_research_calls_search_before_result_validation() -> None:
    provider = FakeSearchProvider(
        results=[
            SearchResult(
                title="Einstein and Relativity",
                url="https://example.com/einstein",
                snippet=(
                    "Einstein developed the theories of special "
                    "and general relativity."
                ),
            )
        ]
    )

    agent = LangChainResearchAgent(
        model=FakeResearchModel(),
        search_provider=provider,
        provenance_validator=ProvenanceValidator(),
    )

    with pytest.raises(
        InvalidEvidenceReferenceError,
        match="evidence-000000000000",
    ):
        await agent.research("Albert Einstein")

    assert provider.queries == [
        "Albert Einstein most significant scientific contribution"
    ]

@pytest.mark.asyncio
async def test_research_rejects_empty_person_name() -> None:
    provider = FakeSearchProvider([])

    agent = LangChainResearchAgent(
        model=FakeResearchModel(),
        search_provider=provider,
        provenance_validator=ProvenanceValidator(),
    )

    with pytest.raises(
        ValueError,
        match="person_name cannot be empty",
    ):
        await agent.research("   ")


# import pytest

# from nn_genai.agents.research_tools import create_search_tool
# from nn_genai.application.research.evidence_ledger import EvidenceLedger
# from nn_genai.infrastructure.agents.langchain_research_agent import (
#     LangChainResearchAgent,
# )
# from nn_genai.models.research_result import ResearchResult
# from nn_genai.models.search_result import SearchResult

# from tests.fakes.fake_research_model import FakeResearchModel
# from tests.fakes.fake_search_provider import FakeSearchProvider


# @pytest.mark.asyncio
# async def test_research_calls_search_and_returns_research_result() -> None:
#     evidence_ledger = EvidenceLedger();
#     provider = FakeSearchProvider(
#         results=[
#             SearchResult(
#                 title="Einstein and Relativity",
#                 url="https://example.com/einstein",
#                 snippet=(
#                     "Einstein developed the theories of special "
#                     "and general relativity."
#                 ),
#             )
#         ]
#     )

#     search_tool = create_search_tool(provider, evidence_ledger)

#     agent = LangChainResearchAgent(
#         model=FakeResearchModel(),
#         search_tool=search_tool,
#     )

#     result = await agent.research("Albert Einstein")

#     assert isinstance(result, ResearchResult)

#     assert result.person_name == "Albert Einstein"
#     assert result.selected_work == "Theory of relativity"
#     assert result.confidence == pytest.approx(0.95)

#     assert len(result.sources) == 1

#     # Critical behavior:
#     # prove that the agent actually executed search_web.
#     assert provider.queries == [
#         "Albert Einstein most significant scientific contribution"
#     ]


# @pytest.mark.asyncio
# async def test_research_rejects_empty_person_name() -> None:
#     provider = FakeSearchProvider([])

#     agent = LangChainResearchAgent(
#         model=FakeResearchModel(),
#         search_tool=create_search_tool(provider),
#     )

#     with pytest.raises(
#         ValueError,
#         match="person_name cannot be empty",
#     ):
#         await agent.research("   ")


# @pytest.mark.asyncio
# async def test_search_web_returns_no_results_message() -> None:
#     provider = FakeSearchProvider([])

#     search_tool = create_search_tool(provider)

#     result = await search_tool.ainvoke(
#         {"query": "Albert Einstein"}
#     )

#     assert result == "No search results found."
#     assert provider.queries == ["Albert Einstein"]
