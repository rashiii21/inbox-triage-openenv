def grade_action(action, gold):
    score = 0.0

    classification = action.get("classification") if isinstance(action, dict) else action.classification
    priority = action.get("priority") if isinstance(action, dict) else action.priority
    decision = action.get("decision") if isinstance(action, dict) else action.decision

    if classification == gold["classification"]:
        score += 0.4

    if priority == gold["priority"]:
        score += 0.3

    if decision == gold["decision"]:
        score += 0.3

    # Clamp strictly between (0, 1)
    if score <= 0:
        return 0.01
    if score >= 1:
        return 0.99

    return float(score)