# Architecture Decision Log

## ADR-001 — Use an async HTTP client

### Decision
Use `httpx` for external HTTP communication.

### Why
The application will eventually make multiple independent network/LLM calls.
An async-compatible client allows us to introduce bounded concurrency later
without redesigning the external API boundary.

### Alternative
Use `requests`.

### Trade-off
`httpx` introduces async complexity for a simple API call, but provides a
better foundation for the eventual workflow.

---

## ADR-002 — Introduce a Person domain model

### Decision
Map the RandomUser API response into a `Person` model.

### Why
The external API schema should not leak into the rest of the application.
A typed model also gives us validation and a stable internal contract.

### Alternative
Pass raw dictionaries through the application.

### Trade-off
The mapping introduces some code, but significantly improves maintainability,
testability and separation of concerns.

---

## ADR-003 — Isolate the RandomUser API behind a client

### Decision
Use `RandomUserApiClient` behind a `RandomUserClient` protocol.

### Why
The application should depend on behavior rather than the concrete HTTP
implementation. This makes the dependency easy to replace or mock in tests.

### Alternative
Call the API directly from `main.py`.

### Trade-off
Slightly more structure for a small assignment, but a much cleaner testing
boundary.

### ADR-004 — Normalize external DOB datetime at the API boundary

### Decision:
Convert RandomUser's ISO datetime DOB into a Python date when mapping
the external response into the Person domain model.

### Why:
The assignment requires birth-date filtering, not time-of-birth semantics.
Keeping date_of_birth as date makes the domain model precise and prevents
the external API representation from leaking into the application.

### Alternative:
Use datetime in Person or add Pydantic conversion logic.

### Trade-off:
The adapter contains a small amount of parsing logic, but this keeps
external-format knowledge isolated and makes the domain model simpler.


## ADR-005 — Separate filtering from formatting

### Decision

Implement filtering and formatting as separate operations in `PersonService`.

### Why

Filtering is application/domain logic while converting people into strings
is a presentation concern. Keeping the `Person` objects after filtering also
allows the same data to be passed to the LLM workflow in Exercise 4.

### Alternative

Use a single function that filters people and immediately returns formatted
strings.

### Trade-off

The implementation has one additional method, but avoids losing information
and gives us a cleaner separation of responsibilities.

---

## ADR-006 — Interpret the year boundary inclusively

### Decision

Keep people where:

    date_of_birth.year <= 2000

and exclude people where:

    date_of_birth.year > 2000

### Why

The assignment says to filter out people "born after the year 2000".
Therefore, anyone born during 2000 remains eligible.

### Alternative

Interpret the requirement as a date cutoff such as
`date_of_birth < 2000-01-01`.

### Trade-off

The year-based implementation directly matches the wording of the
requirement and avoids incorrectly excluding people born during 2000.

---

## ADR-007 — Validate and normalize dates at the API boundary

### Decision

The RandomUser client converts the API's datetime string into a Python
`date` before constructing `Person`.

### Why

`Person` represents a birth date rather than a timestamp. Keeping the
normalization at the external boundary prevents API-specific representation
from leaking into the domain.

### Alternative

Store `datetime` in `Person` or handle conversion inside `Person`.

### Trade-off

The client contains parsing logic, but the domain model remains clean
and precise.


## ADR-008 — Keep live API smoke tests separate from unit tests

### Decision

Use the real RandomUser API for manual/integration smoke testing, but keep
automated tests deterministic and independent of the external service.

### Why

The RandomUser service is an external dependency whose availability and
response can change. Unit tests should remain fast and deterministic.

### Alternative

Have pytest call the real API.

### Trade-off

We don't automatically verify the live service on every test run, but our
test suite remains reliable and fast. A separate smoke test verifies the
actual integration.

---

## ADR-009 — Map only required fields from the external API

### Decision

Extract only the fields required by our application into `Person`.

### Why

The RandomUser API exposes significantly more data than the assignment
requires. Modeling the entire external response would add unnecessary
complexity.

### Alternative

Create a complete RandomUser API DTO hierarchy.

### Trade-off

We lose access to fields we haven't modeled, but we gain a smaller,
more maintainable implementation appropriate for the assessment.

## ADR-010 — Introduce an LLM provider abstraction

### Decision

Define an application-facing LLMProvider protocol instead of coupling
IdentityService to a specific model provider.

### Why

The assignment requires a free LLM provider, but provider availability,
models and rate limits can change. The application should depend on an
LLM capability rather than a vendor SDK.

### Alternative

Instantiate the provider SDK directly inside IdentityService.

### Trade-off

Adds an abstraction for a small assignment, but makes the system easier
to test and allows the provider to be changed without modifying the
application service.

---

## ADR-011 — Use structured LLM output

### Decision

Represent identity results using the Pydantic PersonIdentity model.

### Why

LLM output is probabilistic and free-form text is difficult to consume
reliably. Structured output provides a clear application contract and
allows runtime validation.

### Alternative

Return raw text from the LLM.

### Trade-off

Requires provider/model support for structured output or additional
parsing, but significantly improves reliability.

---

## ADR-012 — Cap Exercise 4 at five people

### Decision

Send at most five eligible people to the LLM.

### Why

The assignment explicitly recommends five people because of free-provider
rate limits.

### Alternative

Send every eligible person.

### Trade-off

Lower coverage, but avoids unnecessary API usage and respects the stated
assessment constraint.

---

## ADR-013 — Perform LLM calls sequentially initially

### Decision

Process the five people sequentially.

### Why

Free-tier providers may impose request-per-minute and concurrency limits.
Sequential execution provides predictable behavior for the assessment.

### Alternative

Use unrestricted asyncio.gather().

### Trade-off

Higher latency, but lower risk of throttling. Bounded concurrency can be
introduced later as a performance optimization.


## ADR-014 — Use Gemini Interactions API

## Decision: 

Use Google's current Gemini Interactions API with gemini-3.6-flash behind our LLMProvider abstraction.

## Why:

gemini-2.5-flash is unavailable to this new API user.
Google currently recommends Interactions API for new Gemini applications.
gemini-3.6-flash is currently supported.
It keeps provider-specific details inside GeminiLLMProvider.
It gives us a more future-proof integration for the later agent exercise.

## Alternative: 
Continue using generateContent with a currently supported model.

## Interview answer:

"Initially I implemented the Gemini adapter against generateContent because it was the straightforward API for a single structured generation call. During the integration test, the provider rejected the selected model for new users. I checked the current Gemini API documentation and found that Google now recommends the Interactions API for new projects, so I updated the adapter rather than simply changing the model ID. The important part is that this change is isolated behind LLMProvider, so the application layer doesn't know or care which Gemini API we're using."

That's a very good engineering story for the interview.

## Trade-off: 

generateContent would require less code change, but it is now considered the legacy interface and we'd immediately be building the assessment against Google's older integration path.

## ADR-014.1 — Migrate Gemini adapter to Interactions API

## Decision: 

Use Gemini Interactions API with gemini-3.6-flash.

## Why: 

The original gemini-2.5-flash model is unavailable to the current API user. Google's current documentation identifies Interactions API as the recommended interface for new Gemini applications.

## Alternative: 

Keep generateContent and change to another available model.

## Trade-off: 

That would require less code change, but would leave the assessment using the API Google now considers legacy. Interactions API also gives us a natural path toward the agent/tool work in Exercise 5.

## Boundary:

The rest of the application remains provider-agnostic through LLMProvider.

## ADR-014.2 — Use Gemini as the free LLM provider

### Decision

Use Google's Gemini API through the official `google-genai` Python SDK.

### Why

Gemini provides free-tier model access, native structured output with
Pydantic, and asynchronous Python support. It also provides a natural
path toward the agentic workflow required in Exercise 5.

### Alternative

Use another free provider or directly couple the application to an LLM SDK.

### Trade-off

The implementation becomes dependent on Gemini at the infrastructure
boundary, but the LLMProvider abstraction prevents that dependency from
leaking into the application layer.

---

## ADR-015 — Pass Person context to the LLM

### Decision

The provider receives the complete Person object rather than only a name.

### Why

Names can be ambiguous. Nationality, country and city provide additional
context that can improve identity resolution.

### Alternative

Send only first name + last name.

### Trade-off

Slightly more input tokens, but potentially better disambiguation.

---

## ADR-016 — Validate all LLM output at the provider boundary

### Decision

Gemini responses must be converted into PersonIdentity before leaving
the provider adapter.

### Why

The LLM is probabilistic. The application should never consume
unvalidated free-form model output.

### Alternative

Return raw text and parse it in IdentityService.

### Trade-off

The provider adapter contains schema-specific logic, but this keeps
LLM-specific concerns isolated from the application layer.

### ADR-017 — Validate LLM output at provider boundary

### Decision: 

GeminiLLMProvider converts the raw Gemini response into PersonIdentity before returning it to the application.

### Why: 

Prevents provider-specific response formats from leaking into the domain/application layers and guarantees that downstream code receives a validated model.

### Alternative:

Return raw Gemini responses and parse them in IdentityService.

### Trade-off: 

Parsing in the service would couple application logic to Gemini's response format and make provider replacement harder.


## ADR-018 — Use an agent for Exercise 5

### Decision

Use a LangChain agent rather than a fixed LLM chain.

### Why

The task requires research where the information required to answer
the question is not known in advance. The agent can decide when and
how to use the search tool and can iteratively gather evidence.

### Alternative

Use a fixed chain:

Person → Search → LLM → Answer.

### Trade-off

Agents introduce additional complexity, latency and non-determinism.
However, this task genuinely benefits from tool selection and iterative
research, making the complexity justified.

## ADR-019 — Give the agent a narrow web-search capability

### Decision

Provide the agent with a web-search tool capable of retrieving
title, URL and snippet information.

### Why

The agent needs external evidence to avoid relying solely on its
pretrained knowledge.

### Alternative

Ask the LLM to answer using its internal knowledge.

### Trade-off

External search adds latency and introduces dependency on a search
provider, but substantially improves factual grounding.

### Constraint

The agent receives only the search capability required for the task.
No unrestricted tools are provided.

Exercise 5
│
├── 1. Define ResearchResult model
│
├── 2. Define SearchResult model
│
├── 3. Define SearchProvider interface
│
├── 4. Choose concrete search provider
│
├── 5. Implement search adapter
│
├── 6. Define ResearchAgent interface
│
├── 7. Implement LangChain agent
│
├── 8. Add structured final output
│
├── 9. Add ResearchService
│
├── 10. Test agent with a fake search provider
│
├── 11. Real web-search smoke test
│
└── 12. Integrate Exercise 4 → Exercise 5

###  018	

Use agent rather than chain	

Research is open-ended and requires iterative search

### 019	

Use Tavily	

Agent-oriented search + native LangChain integration + free tier
### 020	

Give agent only web search	

Minimum capability required; reduces complexity and risk

### 021	

Prefer evidence-backed sources	

Reduce hallucination and unsupported claims

### 022	

Limit search results initially to 5	

Sufficient evidence without unnecessary latency/context

### 023	

Start with basic search	

Lower cost/latency; upgrade only if needed

### 024	

Keep external search behind an application boundary	

Avoid coupling business/application logic to Tavily

### ADR-025 — Tavily adapter

### Decision

Implement TavilySearchProvider as an infrastructure adapter behind SearchProvider.

### Why

Keeps Tavily-specific SDK details out of application code.
Converts external response structures into our own SearchResult.
Allows the search implementation to be replaced later.
Provides a clean seam for unit testing.

### Alternative

Use TavilySearch directly inside ResearchService.

### Trade-off

The adapter introduces a small amount of additional code, but gives us dependency inversion and a cleaner test boundary.

### ADR-026 — Initial search limits

### Decision

Use:

max_results = 5
search_depth = basic
topic = general

### Why

The assignment requires focused research rather than exhaustive crawling. Five results should provide enough evidence for a person's major contribution while keeping latency and context size controlled.

### Alternative

Use advanced search with a larger result set.

### Trade-off

Advanced retrieval could improve research quality but increases cost/latency. We'll only introduce it if the real smoke test demonstrates a need.




### ADR decision ### 

I'd record this one as:

### Decision: 
Use Tavily's synchronous invoke() through asyncio.to_thread() in the adapter.

### Why: 
langchain-tavily 0.2.18's async implementation creates a default aiohttp.ClientSession that fails TLS verification in our Python environment, while its requests path and an explicitly certifi-configured aiohttp client both work.

### Alternative: 

Configure/replace the underlying aiohttp SSL context or upgrade the integration.

### Trade-off: 

We retain an async SearchProvider interface but perform the HTTP call in a worker thread. This avoids blocking the event loop and avoids weakening TLS, at the cost of thread-pool overhead and giving up true async I/O.

### Important: 

This is an infrastructure compatibility decision, not a change to our application architecture.



### ADR-027 — Agent uses application search tool

### Decision

Expose SearchProvider through an application-level search_web LangChain tool rather than passing TavilySearch directly to the agent.

### Why

Preserves our provider abstraction.
Keeps Tavily-specific implementation out of the agent.
Makes the agent tool boundary explicit.
Makes the tool independently testable.
Allows the search provider to be replaced without changing the agent.

### Alternative

Pass LangChain's TavilySearch directly to the agent.

### Trade-off

Our approach adds a thin adapter/tool layer, but gives us substantially better separation of concerns and testability.


### ADR-028 — Use an agent rather than a chain

### Decision

Use a LangChain agent because the research strategy requires dynamic tool selection.

### Why

The number and content of searches cannot be completely predetermined. The model needs to decide what additional evidence is necessary.

### Alternative

Fixed chain:

search candidates → search significance → summarize

### Trade-off

Agents introduce nondeterminism and additional complexity, but that complexity is justified by the assignment's requirement to demonstrate agentic research.

### ADR-029 — Evidence is mandatory

### Decision

ResearchResult requires at least one supporting source.

### Why

The agent must ground its conclusion in retrieved evidence rather than simply relying on model knowledge.

### Alternative

Allow a result without citations.

### Trade-off

A strict evidence requirement can occasionally produce "insufficient evidence," but that's preferable to an unsupported confident answer.

### ADR-030 — Bounded agent execution

### Decision

Limit research to a small number of tool iterations.

### Why

Controls latency, cost, and runaway tool use.

### Alternative

Allow unlimited iterations.

### Trade-off

A hard limit can stop research prematurely, but predictable execution is more valuable for this assessment.



### ADR-031 — Structured research result


### Decision: 
Return a Pydantic ResearchResult containing the selected work, reasoning, evidence sources, and confidence.


### Why:

The research task produces an LLM-generated judgment, so we need a validated, machine-readable contract with explicit evidence.


### Alternative: 

Return the agent's raw string response.


### Trade-off: 

Structured output requires an additional validation/extraction step, but gives us much stronger reliability, testability, and downstream integration.


### ADR-032 — ResearchAgent as application port


### Decision: 

Define ResearchAgent as a Python Protocol.


### Why: 

The application should depend on the capability of researching a person, not on LangChain or Gemini.


### Alternative:

Put AgentExecutor/LangChain types directly into the service layer.


### Trade-off: 

One additional abstraction, but it keeps infrastructure replaceable and makes the component easy to mock in tests.



### ADR-033 — Keep LangChain inside the concrete research-agent adapter

### Decision

Implement LangChainResearchAgent as the infrastructure implementation of the application-level ResearchAgent protocol.

### Why

Exercise 5 explicitly requires a LangChain agent, but the application should remain independent of the framework used to implement the agent.

### Alternative

Expose LangChain's AgentExecutor, BaseChatModel, or agent state directly through the application layer.

### Trade-off

The infrastructure adapter contains framework-specific code, but the application remains replaceable and independently testable.

### ADR-034 — Separate identity LLM and research-agent model capabilities

### Decision

Keep the existing LLMProvider for Exercise 4 identity resolution and use a LangChain-compatible chat model inside the concrete Exercise 5 agent.

### Why

Identity resolution and agentic tool calling are different capabilities. Extending the identity provider purely to support agent orchestration would weaken its abstraction.

### Alternative

Add tool-calling methods to LLMProvider.

### Trade-off

There are two infrastructure paths to Gemini, but each has a precise responsibility and the application remains provider-agnostic.

### ADR-035 — Structured agent output

### Decision

Use ResearchResult as the agent's structured final response.

### Why

The final research result needs deterministic validation and downstream consumption.

### Alternative

Return the agent's final natural-language message.

### Trade-off

Structured output adds framework/model requirements, but substantially improves reliability.



### Decision — Deterministic agent orchestration tests

### Why: 

Unit tests must not depend on Gemini responses, Tavily availability, changing web results, API credentials, quotas, or network connectivity. We therefore fake the LLM's decisions and the SearchProvider, while keeping the real LangChainResearchAgent, LangChain graph, search_web tool, and tool dispatch under test.

### Alternative: 

Run the research-agent tests against real Gemini and Tavily.

### Trade-off: 

The deterministic test cannot prove that Gemini will reliably follow the research prompt in production. That behavior must be validated separately through an integration/smoke test. In exchange, unit tests remain fast, repeatable, inexpensive, and non-flaky.

There's also a strong interview distinction here:

Mocks/fakes verify our code. Smoke tests verify our integrations. Evaluations verify AI behavior.

Those are three different testing concerns, and treating them separately is particularly appropriate for GenAI systems.