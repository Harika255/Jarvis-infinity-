import json
from datetime import datetime, date
from pathlib import Path


class RealWorldTaskManager:
    """Local task manager used by JARVIS for practical day-to-day assistance."""

    def __init__(self, path="data/jarvis_tasks.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, tasks):
        self.path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")

    def add_task(self, title, priority="MEDIUM", deadline=None, category="GENERAL"):
        tasks = self._load()
        task = {
            "id": max([t.get("id", 0) for t in tasks], default=0) + 1,
            "title": title,
            "priority": priority.upper(),
            "deadline": deadline,
            "category": category.upper(),
            "status": "PENDING",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        tasks.append(task)
        self._save(tasks)
        return task

    def complete_task(self, task_id):
        tasks = self._load()
        for task in tasks:
            if task.get("id") == int(task_id):
                task["status"] = "COMPLETED"
                task["completed_at"] = datetime.now().isoformat(timespec="seconds")
                self._save(tasks)
                return task
        return None

    def pending(self):
        return [t for t in self._load() if t.get("status") != "COMPLETED"]

    def all_tasks(self):
        return self._load()

    def prioritize(self):
        priority_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        today = date.today().isoformat()

        def key(task):
            deadline = task.get("deadline") or "9999-12-31"
            deadline_rank = 0 if deadline <= today else 1
            return (priority_rank.get(task.get("priority", "MEDIUM"), 1), deadline_rank, deadline)

        return sorted(self.pending(), key=key)

    def create_student_starter_tasks(self):
        if self.pending():
            return self.pending()
        starters = [
            ("Finish current college project module", "HIGH", "PROJECT"),
            ("Review today's class notes", "MEDIUM", "STUDY"),
            ("Practice 30 minutes of coding", "MEDIUM", "CAREER"),
        ]
        return [self.add_task(t, p, category=c) for t, p, c in starters]
