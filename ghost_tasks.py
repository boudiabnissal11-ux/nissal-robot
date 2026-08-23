# ============================================================
# Ghost Tasks — مهام الشبح
# إدارة المهام اليومية والتذكيرات
# ============================================================

import os
import json
import logging
from datetime import datetime, timedelta
from config import OWNER_NAME, GHOST_NAME

logger = logging.getLogger(__name__)


class GhostTasks:
    """مهام Ghost — إدارة المهام"""

    def __init__(self, memory=None):
        self.memory = memory
        self.tasks_file = os.environ.get("TASKS_FILE", "data/tasks.json")
        self.tasks = []
        self.reminder_interval = int(
            os.environ.get("REMINDER_INTERVAL", "30")
        )
        self._load_tasks()

    def _load_tasks(self):
        """تحميل المهام من الملف"""
        try:
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                logger.info(f"📋 تم تحميل {len(self.tasks)} مهمة")
            else:
                self.tasks = []
                self._save_tasks()
        except Exception as e:
            logger.error(f"❌ خطأ بتحميل المهام: {e}")
            self.tasks = []

    def _save_tasks(self):
        """حفظ المهام بالملف"""
        try:
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            logger.info(f"📋 تم حفظ {len(self.tasks)} مهمة")
        except Exception as e:
            logger.error(f"❌ خطأ بحفظ المهام: {e}")

    def add_task(self, title, description="", priority="medium",
                 due_date=None, category="general", created_by=None):
        """إضافة مهمة جديدة"""
        task = {
            "id": f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "category": category,
            "created_by": created_by or OWNER_NAME,
            "created_at": datetime.now().isoformat(),
            "completed": False,
            "completed_at": None,
            "reminded": False
        }

        self.tasks.append(task)
        self._save_tasks()

        logger.info(f"📋 مهمة جديدة: {title}")
        return task

    def complete_task(self, task_id):
        """إكمال مهمة"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                logger.info(f"✅ مهمة مكتملة: {task['title']}")
                return task

        logger.warning(f"⚠️ مهمة غير موجودة: {task_id}")
        return None

    def delete_task(self, task_id):
        """حذف مهمة"""
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save_tasks()
        logger.info(f"🗑️ مهمة محذوفة: {task_id}")

    def get_pending_tasks(self, category=None):
        """المهام المعلّقة"""
        pending = [t for t in self.tasks if not t["completed"]]

        if category:
            pending = [t for t in pending if t["category"] == category]

        pending.sort(key=lambda x: {
            "high": 0, "medium": 1, "low": 2
        }.get(x["priority"], 1))

        return pending

    def get_overdue_tasks(self):
        """المهام المتأخرة"""
        now = datetime.now().isoformat()
        overdue = []

        for task in self.tasks:
            if (not task["completed"]
                    and task.get("due_date")
                    and task["due_date"] < now):
                overdue.append(task)

        return overdue

    def get_reminders(self):
        """المهام اللي لازم نتذكّرها"""
        now = datetime.now()
        soon = now + timedelta(minutes=self.reminder_interval)
        reminders = []

        for task in self.tasks:
            if task["completed"]:
                continue
            if task.get("reminded") and not task.get("due_date"):
                continue

            if task.get("due_date"):
                due = datetime.fromisoformat(task["due_date"])
                if now <= due <= soon and not task.get("reminded"):
                    reminders.append(task)
                    task["reminded"] = True

        if reminders:
            self._save_tasks()

        return reminders

    def format_tasks_list(self, tasks=None, lang="lb"):
        """تنسيق قائمة المهام"""
        if tasks is None:
            tasks = self.get_pending_tasks()

        if not tasks:
            if lang == "lb":
                return "📋 ما في مهام معلّقة — كل شي منيّف! 👻"
            elif lang == "ar":
                return "📋 لا توجد مهام معلقة — كل شيء ممتاز! 👻"
            else:
                return "📋 No pending tasks — all clear! 👻"

        lines = []
        if lang == "lb":
            lines.append(f"📋 مهامك يا {OWNER_NAME}:")
        elif lang == "ar":
            lines.append(f"📋 مهامك يا {OWNER_NAME}:")
        else:
            lines.append(f"📋 Tasks for {OWNER_NAME}:")

        priority_emoji = {
            "high": "🔴", "medium": "🟡", "low": "🟢"
        }

        for i, task in enumerate(tasks, 1):
            emoji = priority_emoji.get(task["priority"], "⚪")
            status = "✅" if task["completed"] else "⏳"
            due = ""
            if task.get("due_date"):
                due_str = datetime.fromisoformat(
                    task["due_date"]
                ).strftime("%m/%d %H:%M")
                due = f" — 📅 {due_str}"

            lines.append(
                f"  {i}. {emoji} {status} {task['title']}{due}"
            )

        return "\n".join(lines)

    def get_tasks_summary(self, lang="lb"):
        """ملخص المهام"""
        pending = len(self.get_pending_tasks())
        completed = len([t for t in self.tasks if t["completed"]])
        overdue = len(self.get_overdue_tasks())

        if lang == "lb":
            return (f"📋 {pending} معلّقة | ✅ {completed} مكتملة | "
                    f"⚠️ {overdue} متأخرة")
        elif lang == "ar":
            return (f"📋 {pending} معلقة | ✅ {completed} مكتملة | "
                    f"⚠️ {overdue} متأخرة")
        else:
            return (f"📋 {pending} pending | ✅ {completed} done | "
                    f"⚠️ {overdue} overdue")
