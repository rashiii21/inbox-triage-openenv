import os
import json
import urllib.request


API_BASE = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")


def call_llm(prompt):
    url = f"{API_BASE}/v1/chat/completions"

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except Exception as e:
        return {"error": str(e)}


def predict(email):
    prompt = f"""
Classify this email and return JSON with exactly these keys:
classification, priority, decision

Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}
"""

    result = call_llm(prompt)

    try:
        content = result["choices"][0]["message"]["content"].strip()
        return json.loads(content)
    except Exception:
        return {
            "classification": "spam",
            "priority": "low",
            "decision": "archive"
        }


def main():
    email = {
        "sender": "billing@company.com",
        "subject": "Payment failed",
        "body": "Customer payment did not go through."
    }

    print("[START]")

    action = predict(email)

    print("[STEP]")
    print(json.dumps(action))

    print("[END]")


if __name__ == "__main__":
    main()