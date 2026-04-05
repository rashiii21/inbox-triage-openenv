from models import EmailItem, Observation, Action, StepResult
from tasks import TASKS
from graders import grade_action


class InboxTriageEnv:
    def __init__(self, task_name="easy"):
        self.task_name = task_name
        self.task_data = TASKS[task_name]
        self.index = 0
        self.completed = []
        self.done = False
        self.max_steps = len(self.task_data)

    def reset(self, task_name=None):
        if task_name:
            self.task_name = task_name
            self.task_data = TASKS[task_name]

        self.index = 0
        self.completed = []
        self.done = False
        self.max_steps = len(self.task_data)
        return self._get_observation()

    def state(self):
        return self._get_observation()

    def step(self, action: Action):
        if self.done:
            raise ValueError("Episode already finished. Call reset().")

        current = self.task_data[self.index]
        gold = current["gold"]

        reward = grade_action(action, gold)
        self.completed.append(current["email_id"])

        self.index += 1
        if self.index >= len(self.task_data):
            self.done = True
            obs = self._final_observation()
        else:
            obs = self._get_observation()

        return StepResult(
            observation=obs,
            reward=reward,
            done=self.done,
            info={"task_name": self.task_name},
        )

    def _get_observation(self):
        current = self.task_data[self.index]
        return Observation(
            task_name=self.task_name,
            current_email=EmailItem(
                email_id=current["email_id"],
                sender=current["sender"],
                subject=current["subject"],
                body=current["body"],
            ),
            step_count=self.index + 1,
            max_steps=self.max_steps,
            completed=self.completed,
        )

    def _final_observation(self):
        last = self.task_data[-1]
        return Observation(
            task_name=self.task_name,
            current_email=EmailItem(
                email_id=last["email_id"],
                sender=last["sender"],
                subject=last["subject"],
                body=last["body"],
            ),
            step_count=self.max_steps,
            max_steps=self.max_steps,
            completed=self.completed,
        )