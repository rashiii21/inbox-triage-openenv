<<<<<<< HEAD
def grade_action(action, gold):
    score = 0.0

    if action.classification == gold["classification"]:
        score += 0.4

    if action.priority == gold["priority"]:
        score += 0.3

    if action.decision == gold["decision"]:
        score += 0.3

    score = max(0.0, min(1.0, score))
=======
def grade_action(action, gold):
    score = 0.0

    if action.classification == gold["classification"]:
        score += 0.4

    if action.priority == gold["priority"]:
        score += 0.3

    if action.decision == gold["decision"]:
        score += 0.3

    score = max(0.0, min(1.0, score))
>>>>>>> f94e4834fdacd0d3485fb6cabbcdd0cb08d8f285
    return score