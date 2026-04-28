from __future__ import annotations


def classify_event(description: str) -> dict[str, object]:
    text = description.lower()
    event_type = "addition"
    turnover_type = "none"
    successor_origin = "unknown"
    confidence = 0.55

    if any(word in text for word in ["resign", "retire", "depart", "step down", "terminated"]):
        event_type = "turnover"
        turnover_type = "ambiguous"
        confidence = 0.7
    if any(word in text for word in ["successor", "appointed", "promoted", "named"]):
        event_type = "succession"
        confidence = max(confidence, 0.72)
    if any(word in text for word in ["external", "outside", "joined from"]):
        successor_origin = "external"
    if any(word in text for word in ["internal", "promoted", "within"]):
        successor_origin = "internal"
    if any(word in text for word in ["retire", "planned", "voluntary"]):
        turnover_type = "voluntary"
    if any(word in text for word in ["terminated", "removed", "involuntary"]):
        turnover_type = "involuntary"

    rationale = f"Keyword-based classification detected {event_type}"
    if successor_origin != "unknown":
        rationale += f" with {successor_origin} successor signal"
    return {
        "event_type": event_type,
        "turnover_type": turnover_type,
        "successor_origin": successor_origin,
        "llm_confidence": confidence,
        "classification_rationale": rationale,
    }
