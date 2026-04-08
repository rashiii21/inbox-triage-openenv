TASKS = {
    "easy": [
        {
            "email_id": "e1",
            "sender": "billing@company.com",
            "subject": "Payment failed",
            "body": "Customer payment did not go through. Please review the billing issue.",
            "gold": {
                "classification": "billing",
                "priority": "high",
                "decision": "escalate",
            },
        }
    ],
    "medium": [
        {
            "email_id": "e2",
            "sender": "calendar@company.com",
            "subject": "Team meeting tomorrow",
            "body": "Please confirm your availability for tomorrow's team meeting.",
            "gold": {
                "classification": "meeting",
                "priority": "medium",
                "decision": "schedule",
            },
        }
    ],
    "hard": [
        {
            "email_id": "e3",
            "sender": "promo@randomsite.com",
            "subject": "Win a free phone now!!!",
            "body": "Click here right now to claim your free reward and prize.",
            "gold": {
                "classification": "spam",
                "priority": "low",
                "decision": "archive",
            },
        }
    ],
}