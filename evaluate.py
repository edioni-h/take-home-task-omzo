##print the required calculated evaluation metrics

from __future__ import annotations

from evaluation_cases import EVALUATION_CASES
from router import route


RISK_REFLECTION = (
    "The mistakes that worry me most are missed urgent or clinician-only messages because they could delay human care.",
    "False escalations also matter because they burden the care team, but they are safer than allowing the AI to answer a risky message alone.",
    "After safety errors, I would prioritize precedence and unsupported-domain mistakes because they could bypass policy or produce an inappropriate automated answer.",
)


def run_evaluation() -> int:
    rows = []
    for case in EVALUATION_CASES:
        actual = route(case.message)["route"]
        rows.append((case, actual))

    wrong_rows = [
        (case, actual)
        for case, actual in rows
        if actual != case.expected_route
    ]
    correct = len(rows) - len(wrong_rows)
    urgent_rows = [(case, actual) for case, actual in rows if case.urgent]
    urgent_caught = sum(actual == "escalate" for _, actual in urgent_rows)
    non_urgent_rows = [(case, actual) for case, actual in rows if not case.urgent]
    false_escalations = sum(actual == "escalate" for _, actual in non_urgent_rows)
    accuracy = (correct / len(rows)) * 100 if rows else 0.0

    print(f"Overall accuracy: {correct}/{len(rows)} ({accuracy:.1f}%)")
    print(f"Urgent messages caught: {urgent_caught}/{len(urgent_rows)}")
    print(
        "Non-urgent messages wrongly escalated: "
        f"{false_escalations}/{len(non_urgent_rows)}"
    )

    if wrong_rows:
        print("Wrong rows:")
        for case, actual in wrong_rows:
            print(
                f'- id={case.id} expected={case.expected_route} '
                f'actual={actual} message="{case.message}"'
            )
    else:
        print("Wrong rows: none")

    print()
    for sentence in RISK_REFLECTION:
        print(sentence)

    return 1 if wrong_rows else 0


def main() -> int:
    return run_evaluation()


if __name__ == "__main__":
    raise SystemExit(main())
