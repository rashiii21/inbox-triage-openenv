
import json
import os
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENV_URL = os.getenv("ENV_URL", "http://127.0.0.1:7860")
TASK_NAME = os.getenv("TASK_NAME", "easy")

client = OpenAI(api_key=OPENAI_API_KEY, base_url=API_BASE_URL)


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
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def ask_model(email):
    prompt = f"""
You are triaging an email.

Email:
Sender: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Return only JSON with:
email_id, classification, priority, decision
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100,
    )
    return response.choices[0].message.content.strip()


def main():
    rewards = []
    steps = 0
    score = 0.0
    success = False

    log_start(TASK_NAME, "inbox-triage-openenv", MODEL_NAME)

    try:
        reset_res = requests.post(f"{ENV_URL}/reset", json={"task_name": TASK_NAME})
        reset_res.raise_for_status()
        obs = reset_res.json()["observation"]

        fallback_email_id = obs["current_email"]["email_id"]

        try:
            raw = ask_model(obs["current_email"])
            action = parse_action(raw, fallback_email_id)
        except Exception:
            action = {
                "email_id": fallback_email_id,
                "classification": "billing",
                "priority": "high",
                "decision": "escalate",
            }

        step_res = requests.post(f"{ENV_URL}/step", json=action)
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