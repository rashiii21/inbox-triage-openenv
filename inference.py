import os
import requests

API_BASE = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

def call_llm(prompt):
    response = requests.post(
        f"{API_BASE}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
        },
    )
    return response.json()