from __future__ import annotations

from models.lm_tone import score_lm_tone


def score_finbert_sentiment(text: str) -> dict[str, float]:
    """Offline FinBERT-compatible sentiment proxy.

    The portfolio spec calls for an AI-based FinBERT component. This demo keeps
    the same output schema but uses a deterministic proxy so the app runs without
    downloading large model weights. Replace this function with a Hugging Face
    FinBERT pipeline when deployment constraints allow it.
    """
    tone = score_lm_tone(text)
    pos = min(max(0.33 + tone["net_tone"] * 8, 0.02), 0.96)
    neg = min(max(0.33 - tone["net_tone"] * 8 + tone["lm_uncertainty_ratio"] * 2, 0.02), 0.96)
    neutral = max(1 - pos - neg, 0.02)
    total = pos + neg + neutral
    pos, neg, neutral = pos / total, neg / total, neutral / total
    return {
        "finbert_positive": pos,
        "finbert_negative": neg,
        "finbert_neutral": neutral,
        "finbert_net_sentiment": pos - neg,
    }
