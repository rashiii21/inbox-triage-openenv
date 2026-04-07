import json
import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    if not OPENAI_API_KEY:
        return None
    return OpenAI(api_key=OPENAI_API_KEY, base_url=API_BASE_URL)


def parse_action(raw, fallback_email_id):
    if not raw:
        raise ValueError("Empty model response")

    # remove ```json ... ``` if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()

    data = json.loads(raw)

    return {
        "email_id": data.get("email_id", fallback_email_id),
        "classification": data.get("classification", "billing"),
        "priority": data.get("priority", "high"),
        "decision": data.get("decision", "escalate"),
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

Return only valid JSON with these keys:
email_id, classification, priority, decision
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()


def fallback_action(fallback_email_id):
    return {
        "email_id": fallback_email_id,
        "classification": "billing",
        "priority": "high",
        "decision": "escalate",
    }


def main():
    rewards = []
    steps = 0
    score = 0.0
    success = False

    log_start(TASK_NAME, "inbox-triage-openenv", MODEL_NAME)

    try:
        reset_res = requests.post(f"{ENV_URL}/reset", json={"task_name": TASK_NAME}, timeout=30)
        reset_res.raise_for_status()
        obs = reset_res.json()["observation"]

        fallback_email_id = obs["current_email"]["email_id"]

        try:
            raw = ask_model(obs["current_email"])
            action = parse_action(raw, fallback_email_id)
        except Exception:
            action = fallback_action(fallback_email_id)

        step_res = requests.post(f"{ENV_URL}/step", json=action, timeout=30)
        step_res.raise_for_status()
        result = step_res.json()

        if "error" in result:
            raise RuntimeError(result["error"])

        reward = float(result["reward"])
        done = bool(result["done"])
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
