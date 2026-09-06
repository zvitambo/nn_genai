# NN GenAI Assessment

Project: NN GenAI assessment.
src/
└── nn_genai/
    ├── application/
    │   └── ...
    │
    ├── domain/
    │   └── ...
    │
    ├── infrastructure/
    │   ├── llm/
    │   │   └── gemini_provider.py
    │   │
    │   └── search/
    │       └── tavily_search_provider.py
    │
    └── models/
        ├── person.py
        ├── person_identity.py
        ├── search_result.py
        └── research_result.py



src/
└── nn_genai/
    ├── application/
    │   ├── ports/
    │   │   └── search_provider.py
    │   │
    │   └── agents/
    │       └── research_tools.py
    │
    ├── infrastructure/
    │   └── search/
    │       └── tavily_search_provider.py
    │
    └── models/
        └── search_result.py


### SearchProvider

Responsible for:

Obtaining web search results.

### search_web

Responsible for:

Exposing that capability to the LLM in a controlled tool interface.

### ResearchAgent

Responsible for:

Deciding what information is needed, selecting search queries, evaluating retrieved evidence, and determining when sufficient evidence exists.

### IdentityService

Responsible for:

Producing the structured identity information about the person.

### Final application

Responsible for:

Orchestrating the complete workflow.