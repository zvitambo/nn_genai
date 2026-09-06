import hashlib

from langchain_core.tools import tool

from nn_genai.application.ports.search_provider import SearchProvider
from nn_genai.application.research.evidence_ledger import EvidenceLedger
from nn_genai.application.research.url_normalizer import normalize_url
from nn_genai.models.retrieved_evidence import RetrievedEvidence

from collections.abc import Iterable

from nn_genai.application.research.source_quality import (
    classify_source_quality,
)
from nn_genai.models.search_result import SearchResult


def rank_search_results(
    results: Iterable[SearchResult],
) -> list[SearchResult]:
    indexed_results = list(enumerate(results))

    ranked = sorted(
        indexed_results,
        key=lambda item: (
            -int(classify_source_quality(str(item[1].url))),
            item[0],
        ),
    )

    return [result for _, result in ranked]


def create_evidence_id(url: str) -> str:
    normalized_url = normalize_url(url)
    digest = hashlib.sha256(normalized_url.encode("utf-8")).hexdigest()
    return f"evidence-{digest[:12]}"


def create_search_tool(
    search_provider: SearchProvider,
    evidence_ledger: EvidenceLedger,
):
    @tool("search_web")
    async def search_web(query: str) -> str:
        """
            Search the public web for factual information and evidence.
            Use this tool when you need to verify facts, investigate a person's
            contributions, compare claims, or find authoritative sources.
        """

        results = await search_provider.search(query)

        if not results:
            return "No search results found."

        formatted_results: list[str] = []

        ranked_results = rank_search_results(results)

        for index, result in enumerate(ranked_results, start=1):
            normalized_url = normalize_url(str(result.url))
            evidence_id = create_evidence_id(normalized_url)

            evidence = RetrievedEvidence(
                evidence_id=evidence_id,
                title=result.title,
                url=normalized_url,
                snippet=result.snippet,
            )
            evidence_ledger.add(evidence)

            quality = classify_source_quality(str(evidence.url))

            formatted_results.append(
                f"{index}. {result.title}\n"
                f"Evidence ID: {evidence_id}\n"
                f"Source category: {quality.name.lower()}\n"
                f"URL: {normalized_url}\n"
                f"Snippet: {result.snippet}"
            )

        return "\n\n".join(formatted_results)

    return search_web


