from __future__ import annotations

import re

# Curated subset of Loughran-McDonald (2011) finance-domain sentiment dictionaries.
# Full dictionary: https://sraf.nd.edu/loughranmcdonald-master-dictionary/

POSITIVE_WORDS = {
    "able", "abundance", "achieve", "achievement", "advantage", "affirm",
    "allow", "benefit", "best", "better", "breakthrough", "capable",
    "certainty", "collaborate", "collaboration", "commitment", "competency",
    "confidence", "consistent", "constructive", "critical", "deliver",
    "disciplined", "diversify", "dynamic", "effective", "effectively",
    "efficiency", "enable", "enhance", "enhance", "excellence", "exceptional",
    "expand", "expansion", "expedite", "experienced", "favorable",
    "flexibility", "focused", "gained", "generate", "growth",
    "ideal", "improve", "improved", "improvement", "increase", "increased",
    "innovation", "innovative", "invest", "leadership", "leading",
    "maximize", "momentum", "noteworthy", "opportunity", "optimal",
    "outstanding", "outperform", "positive", "profitable", "profitability",
    "progress", "progressive", "promising", "qualified", "readily",
    "recover", "recovery", "resilient", "resolved", "robust", "significant",
    "skilled", "stable", "strength", "strengthen", "strong", "success",
    "successful", "superior", "sustainable", "transparency", "trustworthy",
    "unique", "valuable", "value", "viable", "world-class",
}

NEGATIVE_WORDS = {
    "abandon", "abnormal", "absence", "adverse", "against", "allegation",
    "ambiguity", "bankruptcy", "breach", "burden", "cancel", "cease",
    "challenge", "challenging", "claim", "complaint", "complicate",
    "concern", "condition", "contingency", "curtail", "default",
    "delay", "deteriorate", "diminish", "discontinue", "dispute",
    "disruption", "doubt", "downgrade", "downturn", "erode",
    "failure", "fault", "fine", "fraud", "impair", "impairment",
    "inadequate", "investigation", "lawsuit", "liability", "limitation",
    "liquidate", "litigation", "loss", "low", "material", "misstatement",
    "noncompliance", "obstacle", "penalty", "pressure", "problem",
    "recall", "reduce", "reduction", "regulatory", "rejection",
    "restructure", "restate", "restatement", "risk", "shortage",
    "significant", "slowdown", "terminate", "termination", "uncertain",
    "uncertainty", "unfavorable", "unforeseen", "unsuccessful", "violation",
    "volatile", "vulnerability", "weak", "weakness", "write-down", "write-off",
}

UNCERTAINTY_WORDS = {
    "anticipate", "approximate", "assume", "assumption", "believe",
    "contingent", "could", "depend", "difficult", "doubt", "estimate",
    "eventually", "expect", "fluctuate", "foresee", "generally",
    "hypothetical", "if", "imprecise", "indefinite", "inherent", "intend",
    "likely", "may", "might", "objective", "pending", "plan",
    "possible", "possibly", "potential", "potentially", "predict",
    "projected", "propose", "roughly", "seek", "should", "speculate",
    "subject", "tentative", "uncertain", "uncertainty", "unexpected",
    "unknown", "unpredictable", "variable", "various", "would",
}


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text)]


def score_lm_tone(text: str) -> dict[str, float]:
    tokens = _tokens(text)
    total = max(len(tokens), 1)
    positive = sum(t in POSITIVE_WORDS for t in tokens)
    negative = sum(t in NEGATIVE_WORDS for t in tokens)
    uncertainty = sum(t in UNCERTAINTY_WORDS for t in tokens)
    return {
        "lm_positive_ratio": positive / total,
        "lm_negative_ratio": negative / total,
        "lm_uncertainty_ratio": uncertainty / total,
        "net_tone": (positive - negative) / total,
    }
