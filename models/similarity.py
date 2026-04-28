from __future__ import annotations

import math
import re
from collections import Counter


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "our",
    "the",
    "to",
    "we",
    "with",
}


def _tokens(text: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text)
        if token.lower() not in STOP_WORDS
    ]


def _tf(tokens: list[str]) -> Counter[str]:
    return Counter(tokens)


def pairwise_similarity(previous_text: str, current_text: str) -> float:
    if not previous_text.strip() or not current_text.strip():
        return 0.0
    previous = _tf(_tokens(previous_text))
    current = _tf(_tokens(current_text))
    vocabulary = set(previous) | set(current)
    if not vocabulary:
        return 0.0
    dot = sum(previous[token] * current[token] for token in vocabulary)
    previous_norm = math.sqrt(sum(value * value for value in previous.values()))
    current_norm = math.sqrt(sum(value * value for value in current.values()))
    if previous_norm == 0 or current_norm == 0:
        return 0.0
    return dot / (previous_norm * current_norm)
