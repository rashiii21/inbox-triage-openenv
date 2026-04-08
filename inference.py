import json
import os

import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:7860")
TASK_NAME = os.getenv("TASK_NAME", "easy")


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def get_client():
    if not API_KEY:
        raise RuntimeError("API_KEY missing")
    if not API_BASE_URL:
        raise RuntimeError("API_BASE_URL missing")

    return OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
    )


def parse_action(raw, fallback_email_id):
    if not raw:
        raise ValueError("Empty model response")

    raw = raw.strip()

    if raw.startswith("```"):
        lines = raw.splitlines()
        if len(lines) >= 3:
            raw = "\n".join(lines[1:-1]).strip()

    data = json.loads(raw)

    return {
        "email_id": data.get("email_id", fallback_email_id),
        "classification": data["classification"],
        "priority": data["priority"],
        "decision": data["decision"],
    }


def ask_model(email):
    client = get_client()

    prompt = f"""
You are triaging an email.

Email:
Sender: {email.get('sender', '')}
Subject: {email.get('subject', '')}
Body: {email.get('body', '')}

Return only valid JSON with exactly these keys:
email_id, classification, priority, decision

Allowed values:
- classification: billing, technical, account, general
- priority: low, medium, high
- decision: respond, escalate, ignore
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        max_tokens=100,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Model returned empty content")

    return content.strip()


def main():
    rewards = []
    steps = 0
    score = 0.0
    success = False

    log_start(TASK_NAME, "inbox-triage-openenv", MODEL_NAME)

    try:
        reset_res = requests.post(
            f"{ENV_URL}/reset",
            json={"task_name": TASK_NAME},
            timeout=30,
        )
        reset_res.raise_for_status()

        reset_json = reset_res.json()
        obs = reset_json["observation"]
        current_email = obs["current_email"]

        raw = ask_model(current_email)
        action = parse_action(raw, current_email["email_id"])

        step_res = requests.post(
            f"{ENV_URL}/step",
            json=action,
            timeout=30,
        )
        step_res.raise_for_status()

        result = step_res.json()

        if "error" in result and result["error"]:
            raise RuntimeError(result["error"])

        reward = float(result.get("reward", 0.0))
        done = bool(result.get("done", True))

        rewards.append(reward)
        steps = 1

        action_str = json.dumps(action, separators=(",", ":"))
        log_step(1, action_str, reward, done, None)

        score = max(0.0, min(1.0, reward))
        success = score >= 0.5

    except Exception as e:
        log_step(1, "null", 0.0, True, str(e))

    log_end(success, steps, score, rewards)


if __name__ == "__main__":
    main()