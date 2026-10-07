# Omzo Air Applied AI Engineer Take-Home

This repository contains the system design and deterministic message router requested in the take-home exercise. All messages and personal details in the evaluation data are fake.

## Run everything

Requirements: Python 3.10 or newer. There are no third-party dependencies and nothing to install.

From the repository root, run:

```bash
python -B verify.py
```

The command validates the final file set, strict UTF-8 text, and the two-page design PDF; runs all unit tests; then prints the required evaluation. The expected headline results are:

```text
Overall accuracy: 20/20 (100.0%)
Urgent messages caught: 7/7
Non-urgent messages wrongly escalated: 0/13
Wrong rows: none
```

It exits with a non-zero status if encoding validation, a unit test, or an evaluation row fails. `python -B evaluate.py` can be used for the metrics-only view.

## Routing behavior

`route(message)` returns a dictionary with exactly two fields:

```python
{"route": "escalate", "reason": "Safety rule matched: dose-change request."}
```

Possible routes are `code`, `faq`, `answer`, `refuse`, and `escalate`. Safety is evaluated first, so urgent or clinician-only content always overrides prompt injection, off-topic content, and other intents. Reasons identify the rule category without copying the input message or its fake identifiers.

## Files

- `router.py` - stateless deterministic `route(message)` implementation.
- `evaluation_cases.py` - the 20 supplied fake cases in UTF-8.
- `tests/test_router.py` - required cases plus safety, precedence, normalization, and contract tests.
- `evaluate.py` - calculated metrics, wrong-row reporting, and three-sentence risk reflection.
- `verify.py` - one-command encoding, file-set, test, and evaluation verification.
- `DESIGN.md` - editable source for the one-page Part 1 answer and separate sketch.
- `DESIGN.pdf` - reviewer-friendly two-page render: design prose first, full-page architecture graph second.
- `architecture.svg` - standalone, editable production-architecture graph embedded in `DESIGN.md`.
- `NOTES.md` - timing, decisions, chronological AI prompt record, corrections, limitations, and next steps.

## Scope and limitations

This is a small exercise router, not a medical device or a production clinical classifier. It uses bounded rules rather than an LLM, has no persistence, and considers only the supplied message. It supports the provided French nausea case but does not claim general multilingual safety. The production design separately describes recent safety context and persistent human-handoff state.

The supplied refund case is intentionally routed to `answer` because that is its expected label; a production system would normally use deterministic support or a human workflow and minimize identifiers first. Secure code and HIPAA-eligible services do not by themselves make a platform HIPAA compliant.
