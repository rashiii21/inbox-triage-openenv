from tasks import TASKS

class InboxTriageEnv:
    def __init__(self, task_name="easy"):
        self.task_name = task_name
        self.current_task = None

    def reset(self, task_name="easy"):
        self.task_name = task_name
        self.current_task = TASKS[0] if isinstance(TASKS, list) else TASKS[task_name][0]
        return self._get_observation()

    def step(self, action):
        # your step logic here
        ...

    def state(self):
        # your state logic here
        ...

    def _get_observation(self):
        return {
            "email_id": self.current_task["email_id"],
            "sender": self.current_task["sender"],
            "subject": self.current_task["subject"],
            "body": self.current_task["body"],
        }