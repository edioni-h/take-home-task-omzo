# Notes

All messages and personal details used in this repository are fake and come from the task.

## Time spent

- Part 1 system design and review: approximately 75 minutes.
- Part 2 router, tests, evaluation, documentation, and verification: approximately 90 minutes.

These are rough focused-work estimates and include AI-assisted review.

## Key decisions

1. I put safety checks before every other routing decision. Urgent and clinician-only signals run before injection, off-topic, FAQ, or answer rules. This is why an injection that also asks to double a dose is escalated.
2. I kept the exercise router deterministic and dependency-free. Plain rules are easy to inspect, reproduce, test, and explain within the scope of this exercise. Reasons name the category without repeating message content.
3. I kept the coding exercise stateless but made the production handoff stateful. The design uses recent safety context, an explicit human-handling state, stable idempotency keys, and a transactional outbox. Later messages stay with the same human case and never return to RAG until the care team closes or releases it.

The supplied row 19 is intentionally honored as `answer` for scoring. I think a real refund request should normally use deterministic support or a human workflow, with identifiers minimized before processing.

## Rejected option

I considered using an LLM as the router, but rejected it for this exercise. It would add nondeterminism, latency, cost, external data handling, and a harder-to-explain failure mode without adding much value to a small fixed policy. A separately evaluated classifier may help production paraphrase coverage, but it should not replace clinician-approved safety rules or the persistent handoff gate.

## AI tools and prompts

I used Codex to review the task, challenge the design, help implement the router and tests, and verify the final result. These are three real prompts that changed the solution.

### Prompt 1: safety precedence

For the router, pay special attention to the fact that urgent and clinician-only messages must always be escalated before any other route. For example, a prompt-injection message that also asks to double a dose must be escalated, not only refused. The code should be deterministic and explainable, and route(message) must return both the route and a useful reason.

All provided data is fake, and we must not introduce any real patient or personal data. Keep the design aligned with HIPAA-aware engineering without falsely claiming that code alone makes a platform HIPAA compliant.

I used this prompt to establish the main routing rule: safety must win when a message matches more than one category. It also led to tests for mixed urgent and injection content.

### Prompt 2: correcting the submission plan

Okay, the overall plan makes sense, but before implementing anything, update the blueprint only with these corrections:

1. Fix every encoding issue and require all files to use UTF-8. I do not want corrupted characters or broken French accents anywhere. The French test must use: "Je me sens un peu nauséeux depuis le début du traitement."
2. DESIGN.md must actually fit within one page, excluding the separate sketch. Target roughly 450-550 words and add a final rendered-page verification step.
3. The implementation blueprint is an internal planning document and should not be included in the final reviewer-facing submission.
4. Resolve the model-cost inconsistency. Compare GPT-4.1 Mini and GPT-5.4 Mini, select one as the explicit launch assumption, and update the monthly calculation and redesign trigger to match that model.
5. Keep the repository limited to the files requested in the assignment unless an additional file has a clear technical purpose.

Do not implement yet. Update the blueprint, summarize what changed, and show me the revised model-cost calculation.

This caught several problems before implementation: corrupted multilingual text, an answer that would not reliably fit on one page, inconsistent model assumptions in the cost calculation, and internal planning files that did not belong in the submission.

### Prompt 3: production handoff behavior

I need you to update the production architecture so that:

- The safety router can use recent safety context.
- The conversation stores an explicit handoff state.
- Once escalated, the session remains in human handling until the care team closes or releases it.
- Later patient messages are appended to the same care-team case.
- Messages do not return to RAG or the model while human handling is active.
- Escalation creation uses an idempotency key to prevent duplicate cases.
- A failed queue write does not falsely tell the patient that handoff succeeded.
- Queue failures use a durable retry or outbox path with operational alerting.

Keep the coding exercise stateless and limited to route(message), because adding persistence there would exceed the requested scope. This clarification should affect only the production design and architecture explanation.

Update the blueprint only, explain the revised message flow, and stop before implementing.

This separated the small stateless exercise from the production workflow. The production design now keeps an escalated conversation assigned to the same human case, prevents it from returning to the model, handles retries idempotently, and does not claim that delivery succeeded before it is confirmed.

I reviewed the generated work between each stage instead of accepting a single generated solution. I also checked model names and prices against official documentation. No real patient or personal data was used.

## Where I corrected the AI

The initial production design mentioned durable SQS escalation, but it did not explain whether recent conversation context affected safety or what happened to later messages after escalation. I treated this as a safety gap and asked for explicit handoff state, same-case message appends, authenticated release or closure, idempotent case creation, and truthful handling of queue failures.

I also noticed that the early cost discussion mixed model assumptions. I asked for one named model to be used consistently for both the monthly estimate and the redesign trigger.

During the final audit, I also found that the French evaluation row had gained a period that was not present in the supplied dataset, and that several clear urgent paraphrases were not covered. I restored the exact supplied text and added regression tests for impending fainting, reversed vomiting wording, and dose timing or schedule changes.

And then proceeded to refactor the testing files using subtest instead of doing repetitive wraps for 20 tests.

## What I would do next

- Have clinicians expand and label adversarial, ambiguous, and multilingual safety cases.
- Measure urgent recall and false-escalation load on a larger synthetic set before choosing thresholds.
- Add fuzz and property-based tests for punctuation, Unicode, negation, and mixed intents.
- Test the full production handoff with duplicate deliveries, SQS outages, delayed acknowledgments, dead-letter recovery, and concurrent messages.
- Complete privacy, security, BAA, retention, access-review, incident-response, and disaster-recovery work. This code and architecture do not alone establish HIPAA compliance.
