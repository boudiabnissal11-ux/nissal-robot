# ============================================================
# Ghost Appointments — مواعيد الشبح
# إدارة المواعيد والاجتماعات
# ============================================================

import os
import json
import logging
from datetime import datetime, timedelta
from config import OWNER_NAME, GHOST_NAME

logger = logging.getLogger(__name__)


class GhostAppointments:
    """مواعيد Ghost — إدارة المواعيد"""

    def __init__(self, memory=None):
        self.memory = memory
        self.appointments_file = os.environ.get(
            "APPOINTMENTS_FILE", "data/appointments.json"
        )
        self.appointments = []
        self.reminder_before = int(
            os.environ.get("APPOINTMENT_REMINDER_MINUTES", "15")
        )
        self._load_appointments()

    def _load_appointments(self):
        """تحميل المواعيد من الملف"""
        try:
            os.makedirs(
                os.path.dirname(self.appointments_file), exist_ok=True
            )
            if os.path.exists(self.appointments_file):
                with open(self.appointments_file, "r",
                          encoding="utf-8") as f:
                    self.appointments = json.load(f)
                logger.info(
                    f"📅 تم تحميل {len(self.appointments)} موعد"
                )
            else:
                self.appointments = []
                self._save_appointments()
        except Exception as e:
            logger.error(f"❌ خطأ بتحميل المواعيد: {e}")
            self.appointments = []

    def _save_appointments(self):
        """حفظ المواعيد بالملف"""
        try:
            os.makedirs(
                os.path.dirname(self.appointments_file), exist_ok=True
            )
            with open(self.appointments_file, "w",
                      encoding="utf-8") as f:
                json.dump(
                    self.appointments, f,
                    ensure_ascii=False, indent=2
                )
            logger.info(
                f"📅 تم حفظ {len(self.appointments)} موعد"
            )
        except Exception as e:
            logger.error(f"❌ خطأ بحفظ المواعيد: {e}")

    def add_appointment(self, title, date_time, duration_minutes=60,
                        location="", description="", attendees=None,
                        reminder_minutes=None):
        """إضافة موعد جديد"""
        if reminder_minutes is None:
            reminder_minutes = self.reminder_before

        appointment = {
            "id": f"apt_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "date_time": date_time,
            "duration_minutes": duration_minutes,
            "location": location,
            "description": description,
            "attendees": attendees or [],
            "reminder_minutes": reminder_minutes,
            "created_at": datetime.now().isoformat(),
            "status": "scheduled",
            "reminded": False
        }

        self.appointments.append(appointment)
        self._save_appointments()

        logger.info(f"📅 موعد جديد: {title}")
        return appointment

    def cancel_appointment(self, appointment_id):
        """إلغاء موعد"""
        for apt in self.appointments:
            if apt["id"] == appointment_id:
                apt["status"] = "cancelled"
                self._save_appointments()
                logger.info(f"❌ موعد ملغى: {apt['title']}")
                return apt

        logger.warning(f"⚠️ موعد غير موجود: {appointment_id}")
        return None

    def complete_appointment(self, appointment_id):
        """إكمال موعد"""
        for apt in self.appointments:
            if apt["id"] == appointment_id:
                apt["status"] = "completed"
                self._save_appointments()
                logger.info(f"✅ موعد مكتمل: {apt['title']}")
                return apt

        return None

    def get_upcoming(self, days=7):
        """المواعيد القادمة"""
        now = datetime.now()
        future = now + timedelta(days=days)

        upcoming = []
        for apt in self.appointments:
            if apt["status"] != "scheduled":
                continue
            try:
                apt_dt = datetime.fromisoformat(apt["date_time"])
                if now <= apt_dt <= future:
                    upcoming.append(apt)
            except (ValueError, TypeError):
                continue

        upcoming.sort(key=lambda x: x["date_time"])
        return upcoming

    def get_today_appointments(self):
        """مواعيد اليوم"""
        today = datetime.now().date()
        today_apts = []

        for apt in self.appointments:
            if apt["status"] != "scheduled":
                continue
            try:
                apt_dt = datetime.fromisoformat(apt["date_time"])
                if apt_dt.date() == today:
                    today_apts.append(apt)
            except (ValueError, TypeError):
                continue

        today_apts.sort(key=lambda x: x["date_time"])
        return today_apts

    def get_reminders(self):
        """المواعيد اللي لازم نتذكّرها"""
        now = datetime.now()
        reminders = []

        for apt in self.appointments:
            if apt["status"] != "scheduled":
                continue
            if apt.get("reminded"):
                continue

            try:
                apt_dt = datetime.fromisoformat(apt["date_time"])
                remind_at = apt_dt - timedelta(
                    minutes=apt.get("reminder_minutes",
                                    self.reminder_before)
                )

                if now >= remind_at and now <= apt_dt:
                    reminders.append(apt)
                    apt["reminded"] = True
            except (ValueError, TypeError):
                continue

        if reminders:
            self._save_appointments()

        return reminders

    def format_appointments_list(self, appointments=None, lang="lb"):
        """تنسيق قائمة المواعيد"""
        if appointments is None:
            appointments = self.get_upcoming()

        if not appointments:
            if lang == "lb":
                return "📅 ما في مواعيد — يومك فاضي حبيبي! 👻"
            elif lang == "ar":
                return "📅 لا توجد مواعيد — يومك حر! 👻"
            else:
                return "📅 No appointments — you're free! 👻"

        lines = []
        if lang == "lb":
            lines.append(f"📅 مواعيدك يا {OWNER_NAME}:")
        elif lang == "ar":
            lines.append(f"📅 مواعيدك يا {OWNER_NAME}:")
        else:
            lines.append(f"📅 Appointments for {OWNER_NAME}:")

        status_emoji = {
            "scheduled": "🕐", "completed": "✅",
            "cancelled": "❌"
        }

        for i, apt in enumerate(appointments, 1):
            emoji = status_emoji.get(apt["status"], "⚪")
            try:
                dt = datetime.fromisoformat(apt["date_time"])
                dt_str = dt.strftime("%m/%d %H:%M")
            except (ValueError, TypeError):
                dt_str = "—"

            duration = apt.get("duration_minutes", 60)
            location = apt.get("location", "")
            loc_str = f" 📍{location}" if location else ""

            lines.append(
                f"  {i}. {emoji} {apt['title']} — "
                f"📅 {dt_str} ({duration}د){loc_str}"
            )

        return "\n".join(lines)

    def get_appointments_summary(self, lang="lb"):
        """ملخص المواعيد"""
        today = len(self.get_today_appointments())
        upcoming = len(self.get_upcoming(days=7))
        cancelled = len(
            [a for a in self.appointments if a["status"] == "cancelled"]
        )

        if lang == "lb":
            return (f"📅 {today} اليوم | 📆 {upcoming} الأسبوع | "
                    f"❌ {cancelled} ملغى")
        elif lang == "ar":
            return (f"📅 {today} اليوم | 📆 {upcoming} الأسبوع | "
                    f"❌ {cancelled} ملغى")
        else:
            return (f"📅 {today} today | 📆 {upcoming} this week | "
                    f"❌ {cancelled} cancelled")
