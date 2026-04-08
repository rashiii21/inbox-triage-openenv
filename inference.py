import json
import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=API_BASE_URL)


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
        "classification": data.get("classification", "general"),
        "priority": data.get("priority", "medium"),
        "decision": data.get("decision", "respond"),
    }


def ask_model(email):
    client = get_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY missing")

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
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()


def fallback_action(email):
    email_id = email.get("email_id", "")
    sender = (email.get("sender") or "").lower()
    subject = (email.get("subject") or "").lower()
    body = (email.get("body") or "").lower()
    text = f"{sender} {subject} {body}"

    classification = "general"
    priority = "medium"
    decision = "respond"

    if any(word in text for word in ["invoice", "payment", "refund", "charged", "billing"]):
        classification = "billing"
    elif any(word in text for word in ["bug", "error", "issue", "crash", "not working", "failed"]):
        classification = "technical"
    elif any(word in text for word in ["login", "password", "account", "signin", "verification"]):
        classification = "account"

    if any(word in text for word in ["urgent", "asap", "immediately", "critical", "blocked"]):
        priority = "high"
    elif any(word in text for word in ["whenever", "no rush", "later"]):
        priority = "low"

    if any(word in text for word in ["spam", "unsubscribe", "promotion", "advertisement"]):
        decision = "ignore"
    elif classification == "technical" and priority == "high":
        decision = "escalate"
    elif classification in ["billing", "account"] and priority == "high":
        decision = "escalate"

    return {
        "email_id": email_id,
        "classification": classification,
        "priority": priority,
        "decision": decision,
    }


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

        try:
            raw = ask_model(current_email)
            action = parse_action(raw, current_email["email_id"])
        except Exception:
            action = fallback_action(current_email)

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
