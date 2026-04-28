from __future__ import annotations

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
    "company",
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
        if token.lower() not in STOP_WORDS and len(token) > 2
    ]


def top_keywords(text: str, top_n: int = 8) -> list[str]:
    if not text.strip():
        return []
    tokens = _tokens(text)
    unigrams = Counter(tokens)
    bigrams = Counter(" ".join(pair) for pair in zip(tokens, tokens[1:]))
    combined = unigrams + bigrams
    return [term for term, _ in combined.most_common(top_n)]


def topic_label(keywords: list[str]) -> str:
    if not keywords:
        return "No dominant topic"
    return ", ".join(keywords[:3]).title()


def topic_shift(previous_keywords: list[str], current_keywords: list[str]) -> float:
    previous = set(previous_keywords)
    current = set(current_keywords)
    if not previous and not current:
        return 0.0
    overlap = len(previous & current)
    union = len(previous | current)
    return 1 - overlap / max(union, 1)
