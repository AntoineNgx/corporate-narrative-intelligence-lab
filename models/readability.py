from __future__ import annotations

import re


def _sentence_count(text: str) -> int:
    return max(len(re.findall(r"[.!?]+", text)), 1)


def _words(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text)


def _complex_words(words: list[str]) -> int:
    count = 0
    for word in words:
        syllables = len(re.findall(r"[aeiouyAEIOUY]+", word))
        if syllables >= 3:
            count += 1
    return count


def gunning_fog(text: str) -> float:
    words = _words(text)
    if not words:
        return 0.0
    avg_sentence_length = len(words) / _sentence_count(text)
    complex_ratio = _complex_words(words) / len(words)
    return 0.4 * (avg_sentence_length + 100 * complex_ratio)
