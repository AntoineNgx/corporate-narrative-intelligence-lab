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
    """Normalize whitespace while preserving sentence boundaries."""
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def excerpt(text: str, limit: int = 700) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "..."
