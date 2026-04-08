def grade_action(action, gold):
    score = 0.0

    if action.classification == gold["classification"]:
        score += 0.4

    if action.priority == gold["priority"]:
        score += 0.3

    if action.decision == gold["decision"]:
        score += 0.3

   
    if score <= 0.0:
        score = 0.01
    elif score >= 1.0:
        score = 0.99

    return score