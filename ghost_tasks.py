# ============================================================
# Ghost Tasks — مهام الشبح
# إدارة المهام والقوائم
# ============================================================
import json
import os
from datetime import datetime
from config import OWNER_NAME


class GhostTasks:
    """مهام Ghost — بيتابع ويني نصال شو بدّه"""

    def __init__(self, memory=None, brain=None):
        self.memory = memory
        self.brain = brain
        self.tasks_file = "data/tasks.json"
        self.tasks = []
        self.load()

    def load(self):
        """تحميل المهام"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.tasks = []
        else:
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            self.tasks = []

    def save(self):
        """حفظ المهام"""
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, title, description="", priority="medium",
                 due_date=None, category="general"):
        """إضافة مهمة جديدة"""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "category": category,
            "status": "pending",
            "created_at": str(datetime.now()),
            "completed_at": None
        }
        self.tasks.append(task)
        self.save()

        # علّم الذاكرة
        if self.memory:
            self.memory.learn(
                f"task_{task['id']}",
                title,
                category="tasks",
                source="owner"
            )

        return task

    def complete_task(self, task_id):
        """إكمال مهمة"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = str(datetime.now())
                self.save()
                return task
        return None

    def delete_task(self, task_id):
        """حذف مهمة"""
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save()
        return True

    def get_pending(self, category=None):
        """المهام المعلّقة"""
        pending = [t for t in self.tasks if t["status"] == "pending"]
        if category:
            pending = [t for t in pending if t.get("category") == category]
        return pending

    def get_all(self):
        """كل المهام"""
        return self.tasks

    def get_status(self):
        """حالة المهام"""
        pending = len([t for t in self.tasks if t["status"] == "pending"])
        completed = len([t for t in self.tasks if t["status"] == "completed"])
        return f"✅ {pending} معلّقة | {completed} مكتملة | المجموع: {len(self.tasks)}"
