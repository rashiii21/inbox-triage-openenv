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
        # IMPORTANT: never crash
        return {"error": str(e)}