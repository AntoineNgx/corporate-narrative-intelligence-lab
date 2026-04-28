from __future__ import annotations

import re

POSITIVE_WORDS = {
    "achieve",
    "benefit",
    "collaboration",
    "effective",
    "efficiency",
    "growth",
    "improve",
    "innovation",
    "opportunity",
    "progress",
    "profitable",
    "resilient",
    "strong",
    "success",
    "successful",
}

NEGATIVE_WORDS = {
    "adverse",
    "challenge",
    "decline",
    "delay",
    "disruption",
    "loss",
    "material",
    "pressure",
    "risk",
    "uncertain",
    "weak",
    "weakness",
}

UNCERTAINTY_WORDS = {
    "approximate",
    "contingent",
    "could",
    "estimate",
    "may",
    "might",
    "possible",
    "uncertain",
    "uncertainty",
    "unknown",
}


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text)]


def score_lm_tone(text: str) -> dict[str, float]:
    tokens = _tokens(text)
    total = max(len(tokens), 1)
    positive = sum(token in POSITIVE_WORDS for token in tokens)
    negative = sum(token in NEGATIVE_WORDS for token in tokens)
    uncertainty = sum(token in UNCERTAINTY_WORDS for token in tokens)
    positive_ratio = positive / total
    negative_ratio = negative / total
    uncertainty_ratio = uncertainty / total
    return {
        "lm_positive_ratio": positive_ratio,
        "lm_negative_ratio": negative_ratio,
        "lm_uncertainty_ratio": uncertainty_ratio,
        "net_tone": positive_ratio - negative_ratio,
    }
