from __future__ import annotations

import re
from dataclasses import dataclass


SECTION_LABELS = {
    "business_description": "Business Description",
    "mda": "MD&A",
    "both": "Business Description + MD&A",
}


@dataclass(frozen=True)
class FilingInput:
    company_name: str
    ticker: str
    fiscal_year: int
    section: str
    text: str


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_xml_text(raw: str, max_words: int = 10_000) -> str:
    """Remove financial-table noise and deduplicate lines from XML-extracted 10-K text."""
    seen: set[str] = set()
    kept: list[str] = []
    for line in raw.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if len(line.split()) < 8:
            continue
        alpha = sum(c.isalpha() for c in line)
        if alpha / max(len(line), 1) < 0.55:
            continue
        lower = sum(c.islower() for c in line)
        if lower / max(alpha, 1) < 0.4:
            continue
        if line in seen:
            continue
        seen.add(line)
        kept.append(line)
    words = " ".join(kept).split()
    return " ".join(words[:max_words])


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def excerpt(text: str, limit: int = 700) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "..."
