"""Deterministic, explicitly provisional MamakConfidence proxy."""

import re
from collections.abc import Sequence

from .contracts import ConfidenceResult, CriterionScore, RedFlag

FORMULA_VERSION = "1.0"
MARKER = re.compile(
    r"(?:\d|[$€£¥%]|https?://|\b(?:according to|survey of|pilot with|research by|reported by)\b)",
    re.I,
)


def has_evidence_marker(text: str) -> bool:
    return bool(MARKER.search(text))


def calculate_confidence(
    scores: Sequence[CriterionScore], flags: Sequence[RedFlag], *, expose: bool
) -> ConfidenceResult:
    denominator = max(1, len(scores))
    coverage = 100 * sum(bool(item.evidence_quote.strip()) for item in scores) / denominator
    strength = 100 * sum(has_evidence_marker(item.evidence_quote) for item in scores) / denominator
    penalty = sum(
        {"low": 2, "medium": 6, "high": 12, "critical": 12}[item.severity] for item in flags
    )
    value = round(max(0.0, min(100.0, 0.60 * coverage + 0.40 * strength - penalty)), 1)
    return ConfidenceResult(
        value=value if expose else None,
        formula_version=FORMULA_VERSION,
        components={
            "coverage": round(coverage, 1),
            "strength": round(strength, 1),
            "penalty": penalty,
        },
    )
