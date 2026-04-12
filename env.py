from tasks import TASKS


class InboxTriageEnv:
    def __init__(self, task_name="easy"):
        self.task_name = task_name
        self.current_task = None
        self.current_index = 0

    def reset(self, task_name="easy"):
        self.task_name = task_name

        if isinstance(TASKS, list):
            if self.current_index >= len(TASKS):
                self.current_index = 0
            self.current_task = TASKS[self.current_index]
        else:
            if task_name not in TASKS or not TASKS[task_name]:
                raise ValueError(f"Unknown or empty task group: {task_name}")
            self.current_task = TASKS[task_name][0]

        return self._get_observation()

    def step(self, action):
        gold = self.current_task["gold"]
        done = True

        result = {
            "action": {
                "classification": getattr(action, "classification", None),
                "priority": getattr(action, "priority", None),
                "decision": getattr(action, "decision", None),
            },
            "gold": gold,
            "done": done,
        }

        if isinstance(TASKS, list):
            self.current_index += 1

        return result

    def state(self):
        return {
            "task_name": self.task_name,
            "current_task": self.current_task["email_id"] if self.current_task else None,
            "index": self.current_index,
        }

    def _get_observation(self):
        return {
            "email_id": self.current_task["email_id"],
            "sender": self.current_task["sender"],
            "subject": self.current_task["subject"],
            "body": self.current_task["body"],
        }