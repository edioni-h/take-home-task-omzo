##deterministic message router for the Omzo Air take-home exercise

from __future__ import annotations

import re
import unicodedata
from typing import Literal, Pattern, TypedDict


RouteName = Literal["code", "faq", "answer", "refuse", "escalate"]


class RouteResult(TypedDict):
    route: RouteName
    reason: str


RuleGroup = tuple[str, tuple[Pattern[str], ...]]


def _patterns(*expressions: str) -> tuple[Pattern[str], ...]:
    return tuple(re.compile(expression) for expression in expressions)


_SAFETY_RULES: tuple[RuleGroup, ...] = (
    (
        "Safety rule matched: chest pain or pressure.",
        _patterns(r"\bchest\s+(?:pain|pressure|tightness|hurts?|aching)\b"),
    ),
    (
        "Safety rule matched: trouble breathing.",
        _patterns(
            r"\b(?:trouble|difficulty)\s+breathing\b",
            r"\b(?:cannot|can not|can't|cant)\s+breathe\b",
            r"\bshort(?:ness)?\s+of\s+breath\b",
            r"\bbreathless\b",
        ),
    ),
    (
        "Safety rule matched: fainting.",
        _patterns(
            r"\b(?:fainted|fainting)\b",
            r"\b(?:passed|passing)\s+out\b",
            r"\b(?:going|about)\s+to\s+pass\s+out\b",
            r"\b(?:blacked|blacking)\s+out\b",
            r"\blost\s+consciousness\b",
            r"\bfeel(?:ing)?\s+faint\b",
        ),
    ),
    (
        "Safety rule matched: severe or constant stomach pain.",
        _patterns(
            r"\b(?:severe|constant|unbearable|intense)\s+(?:stomach|abdominal|abdomen|belly)\s+pain\b",
            r"\b(?:severe|constant|unbearable|intense)\s+pain\s+(?:in|around)\s+(?:my\s+)?(?:stomach|abdomen|belly)\b",
            r"\b(?:stomach|abdominal|abdomen|belly)\s+pain\b.{0,30}\b(?:severe|constant|unbearable|intense)\b",
        ),
    ),
    (
        "Safety rule matched: vomiting that will not stop.",
        _patterns(
            r"\b(?:vomit(?:ing|ed)?|throwing\s+up)\b.{0,60}\b(?:all\s+day|nonstop|constant(?:ly)?|will\s+not\s+stop|won't\s+stop|wont\s+stop|cannot\s+stop|can't\s+stop|cant\s+stop)\b",
            r"\b(?:cannot|can\s+not|can't|cant|unable\s+to|won't|wont)\s+stop\s+(?:vomiting|throwing\s+up)\b",
            r"\b(?:cannot|can\s+not|can't|cant|unable\s+to)\s+keep\s+(?:water|fluids?|liquids?)\s+down\b",
            r"\bkeep(?:ing)?\s+(?:vomiting|throwing\s+up)\b",
        ),
    ),
    (
        "Safety rule matched: signs of an allergic reaction.",
        _patterns(
            r"\ballergic\s+reaction\b",
            r"\b(?:face|facial|throat|tongue|lips?)\b.{0,40}\b(?:swelling|swollen)\b",
            r"\b(?:swelling|swollen)\b.{0,40}\b(?:face|facial|throat|tongue|lips?)\b",
        ),
    ),
    (
        "Safety rule matched: self-harm concern.",
        _patterns(
            r"\b(?:suicidal|suicide|self[- ]?harm)\b",
            r"\b(?:kill(?:ing)?|hurt(?:ing)?|harm(?:ing)?)\s+myself\b",
            r"\bend\s+my\s+life\b",
            r"\bdon't\s+want\s+to\s+(?:live|be\s+here)\b",
            r"\bthoughts?\s+of\s+(?:suicide|self[- ]?harm|hurting\s+myself|harming\s+myself|ending\s+my\s+life)\b",
            r"\bwhat(?:'s|s|\s+is)\s+the\s+point\s+of\s+(?:anything|living|life)(?:\s+anymore)?\b",
            r"\bno\s+point\s+(?:in|to)\s+(?:living|anything)\b",
        ),
    ),
    (
        "Safety rule matched: pregnancy or possible pregnancy.",
        _patterns(r"\bpregnan(?:t|cy)\b"),
    ),
    (
        "Safety rule matched: dose-change request.",
        _patterns(
            r"\b(?:double|increase|decrease|lower|raise|reduce|change|adjust|skip|delay|move|switch|go\s+up|go\s+down)\b.{0,60}\b(?:my\s+|the\s+|this\s+|next\s+)?(?:dose|dosage|shot|injection)\b",
            r"\b(?:higher|lower|larger|smaller|different|half)\b.{0,35}\b(?:dose|dosage)\b",
            r"\b(?:dose|dosage|shot|injection)\b.{0,80}\b(?:double|increase|decrease|lower|raise|reduce|change|adjust|skip|delay|move|switch|take\s+(?:two|2|half|an\s+extra|another|more|less))\b",
            r"\b(?:take|use|inject)\s+(?:two|2|half|an\s+extra|another|more|less)\b.{0,40}\b(?:dose|dosage|today|tomorrow)\b",
            r"\b(?:take|use|inject)\b.{0,40}\b(?:my\s+|the\s+)?(?:dose|dosage|shot|injection)\b.{0,40}\b(?:later|earlier|tomorrow|instead)\b",
            r"\b(?:change|adjust|skip|delay|move)\b.{0,40}\b(?:dosing\s+|dose\s+)?schedule\b",
            r"\b(?:change|adjust|increase|decrease|lower|raise|reduce)\b.{0,40}\b(?:how\s+much|amount)\b.{0,40}\b(?:i\s+)?(?:inject|take|use)\b",
            r"\b(?:missed|forgot)\b.{0,40}\b(?:dose|shot|injection)\b.{0,80}\b(?:take|use|inject|double|skip)\b",
        ),
    ),
)


_INJECTION_RULES = _patterns(
    r"\bignore\b.{0,50}\b(?:instructions?|rules?|polic(?:y|ies))\b",
    r"\b(?:show|reveal|print|display)\b.{0,40}\bsystem\s+prompt\b",
    r"\b(?:bypass|override)\b.{0,40}\b(?:instructions?|rules?|polic(?:y|ies)|safety)\b",
)


_CODE_RULES: tuple[RuleGroup, ...] = (
    (
        "Deterministic handler matched: greeting.",
        _patterns(
            r"^(?:hi|hello|hey)(?:[,\s]+(?:there|how\s+are\s+you))?[!.?]*$",
            r"^good\s+(?:morning|afternoon|evening)(?:[,\s]+(?:there|how\s+are\s+you))?[!.?]*$",
        ),
    ),
    (
        "Deterministic handler matched: order status.",
        _patterns(
            r"\bwhere\s+(?:is|'s)\s+my\s+(?:order|package|delivery)\b",
            r"\bwhere\s+(?:my\s+|the\s+)?(?:order|package|delivery)\s+is\b",
            r"\b(?:track|tracking|status\s+of)\b.{0,35}\b(?:order|package|delivery)\b",
            r"\b(?:order|package|delivery)\b.{0,35}\b(?:status|tracking|arrive|arrival)\b",
        ),
    ),
    (
        "Deterministic handler matched: appointment request.",
        _patterns(
            r"\b(?:when|where|what\s+time)\b.{0,45}\b(?:my\s+|the\s+)?(?:next\s+)?appointment\b",
            r"\b(?:next|upcoming)\s+appointment\b",
            r"\b(?:book|schedule|reschedule|cancel)\b.{0,35}\bappointment\b",
        ),
    ),
)


_OFF_TOPIC_RULES = _patterns(
    r"\b(?:laptop|computer)\b.{0,30}\b(?:coding|programming|buy|best)\b",
    r"\b(?:best|buy|recommend)\b.{0,30}\b(?:laptop|computer)\b",
    r"\b(?:write|make|compose)\b.{0,40}\b(?:poem|song|story|joke)\b",
)


_ANSWER_RULES: tuple[RuleGroup, ...] = (
    (
        "Supported answer topic matched: product handling question.",
        _patterns(
            r"\b(?:ice|gel)\s+pack\b",
            r"\bcold[- ]chain\b",
        ),
    ),
    (
        "Supported answer topic matched: non-urgent health question.",
        _patterns(
            r"\bnause(?:a|ous|ated|ating|eux|euse)?\b",
            r"\b(?:side\s+effects?|symptoms?|headaches?)\b",
        ),
    ),
    (
        "Supported answer topic matched: wearable question.",
        _patterns(
            r"\b(?:sleep\s+score|resting\s+heart\s+rate|heart\s+rate|wearable|step\s+count|activity\s+score)\b",
        ),
    ),
    (
        "Supported answer topic matched: refund request.",
        _patterns(r"\brefund\b"),
    ),
)


_PEN_PATTERN = re.compile(r"\bpen\b")
_STORAGE_PATTERN = re.compile(r"\b(?:store|storage|keep)\b")
_AFTER_OPENING_PATTERN = re.compile(
    r"\b(?:after\s+(?:opening|i\s+open)|once\s+(?:opened|open)|opened)\b"
)


def _normalize(message: str) -> str:
    normalized = unicodedata.normalize("NFKC", message).translate(
        str.maketrans({"’": "'", "‘": "'", "`": "'"})
    )
    normalized = unicodedata.normalize("NFKD", normalized.casefold())
    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    return " ".join(without_accents.split())


def _first_reason(text: str, rules: tuple[RuleGroup, ...]) -> str | None:
    for reason, patterns in rules:
        if any(pattern.search(text) for pattern in patterns):
            return reason
    return None


def _result(route_name: RouteName, reason: str) -> RouteResult:
    return {"route": route_name, "reason": reason}


def route(message: str) -> RouteResult:
    ##return the deterministic route and category-level reason for one message

    if not isinstance(message, str):
        raise TypeError("message must be a string")

    text = _normalize(message)
    if not text:
        return _result("refuse", "No supported request was provided.")

    safety_reason = _first_reason(text, _SAFETY_RULES)
    if safety_reason:
        return _result("escalate", safety_reason)

    if any(pattern.search(text) for pattern in _INJECTION_RULES):
        return _result("refuse", "Policy rule matched: prompt manipulation request.")

    code_reason = _first_reason(text, _CODE_RULES)
    if code_reason:
        return _result("code", code_reason)

    if (
        _PEN_PATTERN.search(text)
        and _STORAGE_PATTERN.search(text)
        and _AFTER_OPENING_PATTERN.search(text)
    ):
        return _result("faq", "Approved FAQ matched: pen storage after opening.")

    if any(pattern.search(text) for pattern in _OFF_TOPIC_RULES):
        return _result("refuse", "Unsupported topic matched: off-topic request.")

    answer_reason = _first_reason(text, _ANSWER_RULES)
    if answer_reason:
        return _result("answer", answer_reason)

    return _result("refuse", "No supported request category matched.")
