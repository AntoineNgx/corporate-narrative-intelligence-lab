from __future__ import annotations


def abnormal_change_score(row: dict) -> tuple[bool, str, float]:
    score = 0.0
    reasons: list[str] = []

    similarity_drop = abs(float(row.get("similarity_drop", 0)))
    delta_tone = abs(float(row.get("delta_net_tone", 0)))
    delta_finbert = abs(float(row.get("delta_finbert_sentiment", 0)))
    delta_fog = abs(float(row.get("delta_fog_index", 0)))
    topic_shift_score = abs(float(row.get("topic_shift_score", 0)))
    roa_change = abs(float(row.get("roa_change", 0) or 0))
    has_event = bool(row.get("has_leadership_event", False))

    if similarity_drop >= 0.55:
        score += 2.0
        reasons.append("large similarity drop")
    elif similarity_drop >= 0.35:
        score += 1.0
        reasons.append("moderate similarity drop")

    if delta_tone >= 0.025 or delta_finbert >= 0.2:
        score += 1.0
        reasons.append("tone moved sharply")

    if delta_fog >= 3.0:
        score += 1.0
        reasons.append("readability changed materially")

    if topic_shift_score >= 0.65:
        score += 1.0
        reasons.append("topic focus shifted")

    if roa_change >= 0.02:
        score += 0.5
        reasons.append("ROA changed")

    if has_event:
        score += 0.75
        reasons.append("leadership event in same year")

    flag = score >= 2.5
    if not reasons:
        reasons.append("stable narrative profile")
    return flag, "; ".join(reasons), score
