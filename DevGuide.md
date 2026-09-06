we approach this exactly like a senior engineer preparing for the panel:

### Phase 1 — Reverse-engineer the assessment

We'll establish:

Requirement → expected behavior → engineering concern → likely interview question

for all five exercises.

### Phase 2 — Design the solution

We'll decide:

project structure
models
interfaces
API client
LLM abstraction
prompts
agent/tool architecture
error strategy
testing strategy
caching
concurrency
observability

### Phase 3 — Implement the minimum solution

Build the actual .py project.

### Phase 4 — Add the "senior engineer" layer

Not unnecessary complexity, but:

typing
validation
retries
timeouts
structured LLM output
controlled concurrency
caching
logging
configuration
security considerations

### Phase 5 — Test it aggressively

Not just happy paths.

### Phase 6 — Build the presentation

The presentation will explain decisions, not just screenshots of code.

### Phase 7 — Mock the interview

This is the part I think could be particularly valuable.

I'll act as the NN panel and challenge you with questions such as:

“Why did you use an agent here instead of a deterministic workflow?”

“Your LLM says this person is Einstein. How do you know that's actually true?”

“What happens when the LLM provider starts returning 429s?”

“Why did you choose synchronous execution?”

“How would you take this from five people to 50,000?”

“Where would you put this in Azure?”

“What would you monitor in production?”

“What would you test that you haven't tested here?”

And we'll make sure you can answer those from first principles, not memorize talking points.

That approach is particularly well matched to this vacancy because NN describes the role as delivering complex, reusable AI solutions independently, while also emphasizing testing, security, monitoring, performance and agentic frameworks.

My recommendation: let's treat the assignment as a small production-grade GenAI asset, with the implementation deliberately kept simple enough that you can defend every decision. That is much more likely to impress this panel than simply satisfying the five numbered exercises.








### Remaining work

Once provenance passes, the practical remaining sequence is:

### Finalize source-quality preference.

Prefer primary and authoritative sources through ranking and prompting, without pretending domain type alone proves claim quality.

### Define insufficient-evidence behavior.

The agent must fail explicitly or return an inconclusive outcome instead of silently using pretrained knowledge.

### Add operational hardening.

Verify timeouts, retries, logging, configuration, secret handling, and controlled agent iteration.

### Add lightweight observability.

Record search count, latency, selected sources, failure category, and perhaps token usage without logging secrets or excessive personal data.

### Run final test and smoke-test passes.

### Build the presentation.