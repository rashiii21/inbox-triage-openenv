from typing import Literal, Optional, List
from pydantic import BaseModel


# Represents one email
class EmailItem(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str


# What the agent sees (observation)
class Observation(BaseModel):
    task_name: str
    current_email: EmailItem
    step_count: int
    max_steps: int
    completed: List[str]


# What the agent does (action)
class Action(BaseModel):
    email_id: str
    classification: Literal["billing", "technical", "meeting", "spam"]
    priority: Literal["low", "medium", "high"]
    decision: Literal["archive", "reply", "escalate", "schedule"]


# Reward info (extra explanation)
class Reward(BaseModel):
    score: float
    reason: str


# Result of each step
class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict