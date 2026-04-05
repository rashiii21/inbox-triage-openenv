---
title: Inbox Triage OpenEnv
emoji: 📥
sdk: docker
app_port: 7860
tags:
  - openenv
---

# Inbox Triage OpenEnv

A beginner-friendly OpenEnv environment for email triage.

## Motivation

Humans often sort emails by type, urgency, and next action.  
This environment simulates that real-world workflow.

## Observation Space

The agent sees:
- task name
- current email id
- sender
- subject
- body
- current step
- max steps
- completed emails

## Action Space

The agent predicts:
- classification: billing, technical, meeting, spam
- priority: low, medium, high
- decision: archive, reply, escalate, schedule

## Tasks

### Easy
Billing issue email.

### Medium
Meeting scheduling email.

### Hard
Spam email.

## Reward Function

- 0.4 for correct classification
- 0.3 for correct priority
- 0.3 for correct decision

Total score is clamped to the range 0.0 to 1.0.

## API Endpoints

- `POST /reset`
- `POST /step`
- `GET /state`

## Local Setup

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860

## Baseline Scores

Local fallback baseline for easy task:
- easy: 1.00

Live OpenAI API baseline was blocked during testing by account quota limits.