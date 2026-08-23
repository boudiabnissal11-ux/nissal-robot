# ============================================================
# Ghost Appointments — مواعيد الشبح
# إدارة المواعيد والتذكير
# ============================================================
import json
import os
from datetime import datetime, timedelta
from config import OWNER_NAME


class GhostAppointments:
    """مواعيد Ghost — بيعمل منبه لنصال"""

    def __init__(self, memory=None, brain=None):
        self.memory = memory
        self.brain = brain
        self.appointments_file = "data/appointments.json"
        self.appointments = []
        self.load()

    def load(self):
        """تحميل المواعيد"""
        if os.path.exists(self.appointments_file):
            try:
                with open(self.appointments_file, "r", encoding="utf-8") as f:
                    self.appointments = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.appointments = []
        else:
            os.makedirs(os.path.dirname(self.appointments_file), exist_ok=True)
            self.appointments = []

    def save(self):
        """حفظ المواعيد"""
        os.makedirs(os.path.dirname(self.appointments_file), exist_ok=True)
        with open(self.appointments_file, "w", encoding="utf-8") as f:
            json.dump(self.appointments, f, ensure_ascii=False, indent=2)

    def add_appointment(self, title, date_time, location="",
                         description="", reminder_minutes=15,
                         category="general"):
        """إضافة موعد جديد"""
        appointment = {
            "id": len(self.appointments) + 1,
            "title": title,
            "date_time": date_time,
            "location": location,
            "description": description,
            "reminder_minutes": reminder_minutes,
            "category": category,
            "status": "upcoming",
            "created_at": str(datetime.now()),
        }
        self.appointments.append(appointment)
        self.save()

        # علّم الذاكرة
        if self.memory:
            self.memory.learn(
                f"appointment_{appointment['id']}",
                f"{title} — {date_time}",
                category="appointments",
                source="owner"
            )

        return appointment

    def cancel_appointment(self, appointment_id):
        """إلغاء موعد"""
        for appt in self.appointments:
            if appt["id"] == appointment_id:
                appt["status"] = "cancelled"
                self.save()
                return appt
        return None

    def delete_appointment(self, appointment_id):
        """حذف موعد"""
        self.appointments = [
            a for a in self.appointments if a["id"] != appointment_id
        ]
        self.save()
        return True

    def get_upcoming(self, days=7, category=None):
        """المواعيد القادمة"""
        now = datetime.now()
        future = now + timedelta(days=days)
        upcoming = []
        for appt in self.appointments:
            if appt["status"] != "cancelled":
                try:
                    appt_dt = datetime.fromisoformat(appt["date_time"])
                    if now <= appt_dt <= future:
                        upcoming.append(appt)
                except (ValueError, TypeError):
                    continue
        if category:
            upcoming = [a for a in upcoming
                       if a.get("category") == category]
        return sorted(upcoming, key=lambda a: a.get("date_time", ""))

    def get_all(self):
        """كل المواعيد"""
        return self.appointments

    def check_reminders(self):
        """تحقق من التذكيرات"""
        now = datetime.now()
        reminders = []
        for appt in self.appointments:
            if appt["status"] != "cancelled":
                try:
                    appt_dt = datetime.fromisoformat(appt["date_time"])
                    reminder_time = appt_dt - timedelta(
                        minutes=appt.get("reminder_minutes", 15)
                    )
                    if now >= reminder_time and now < appt_dt:
                        reminders.append(appt)
                except (ValueError, TypeError):
                    continue
        return reminders

    def get_status(self):
        """حالة المواعيد"""
        upcoming = len([a for a in self.appointments
                       if a["status"] == "upcoming"])
        cancelled = len([a for a in self.appointments
                        if a["status"] == "cancelled"])
        return f"✅ {upcoming} قادمة | {cancelled} ملغاة | المجموع: {len(self.appointments)}"
