from typing import Dict, Any, List


def compute_confidence(
    *,
    validation_passed: bool,
    repair_attempted: bool,
    repair_succeeded: bool,
    obligations: List[Dict[str, Any]],
    risks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compute confidence score based on observable system behavior.
    Returns score, band, and reasons.
    """

    score = 1.0
    reasons = []

    # 1. Validation
    if not validation_passed:
        score -= 0.4
        reasons.append("Schema validation failed initially")

    # 2. Repair penalty
    if repair_attempted:
        score -= 0.2
        reasons.append("Output required structural repair")

        if not repair_succeeded:
            score -= 0.3
            reasons.append("Repair did not fully succeed")

    # 3. Evidence coverage
    evidence_count = 0
    claim_count = 0

    for o in obligations:
        claim_count += 1
        if o.get("evidence", {}).get("quote"):
            evidence_count += 1

    for r in risks:
        claim_count += 1
        if r.get("evidence", {}).get("quote"):
            evidence_count += 1

    if claim_count > 0:
        coverage = evidence_count / claim_count
        if coverage < 0.5:
            score -= 0.2
            reasons.append("Low evidence coverage for claims")
        elif coverage < 0.8:
            score -= 0.1
            reasons.append("Partial evidence coverage")

    # Clamp
    score = max(0.0, min(1.0, round(score, 2)))

    if score >= 0.8:
        band = "High"
    elif score >= 0.5:
        band = "Medium"
    else:
        band = "Low"

    return {
        "score": score,
        "band": band,
        "reasons": reasons,
    }
