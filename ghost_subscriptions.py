# ============================================================
# Ghost Subscriptions — اشتراكات الشبح
# إدارة الاشتراكات والتذكير
# ============================================================
import json
import os
from datetime import datetime, timedelta
from config import OWNER_NAME, NS_LINKS, SUB_REMINDER_DAYS


class GhostSubscriptions:
    """اشتراكات Ghost — بيعمل تذكير لنصال عن الاشتراكات"""

    def __init__(self, memory=None, brain=None):
        self.memory = memory
        self.brain = brain
        self.subscriptions_file = "data/subscriptions.json"
        self.subscriptions = []
        self.load()

    def load(self):
        """تحميل الاشتراكات"""
        if os.path.exists(self.subscriptions_file):
            try:
                with open(self.subscriptions_file, "r", encoding="utf-8") as f:
                    self.subscriptions = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.subscriptions = []
        else:
            os.makedirs(os.path.dirname(self.subscriptions_file), exist_ok=True)
            self.subscriptions = []

    def save(self):
        """حفظ الاشتراكات"""
        os.makedirs(os.path.dirname(self.subscriptions_file), exist_ok=True)
        with open(self.subscriptions_file, "w", encoding="utf-8") as f:
            json.dump(self.subscriptions, f, ensure_ascii=False, indent=2)

    def add_subscription(self, name, amount, currency="USD",
                          billing_cycle="monthly", next_billing=None,
                          category="general", notes=""):
        """إضافة اشتراك جديد"""
        subscription = {
            "id": len(self.subscriptions) + 1,
            "name": name,
            "amount": amount,
            "currency": currency,
            "billing_cycle": billing_cycle,
            "next_billing": next_billing,
            "category": category,
            "notes": notes,
            "status": "active",
            "created_at": str(datetime.now()),
        }
        self.subscriptions.append(subscription)
        self.save()

        # علّم الذاكرة
        if self.memory:
            self.memory.learn(
                f"sub_{subscription['id']}",
                f"{name} — {amount} {currency}/{billing_cycle}",
                category="subscriptions",
                source="owner"
            )

        return subscription

    def cancel_subscription(self, sub_id):
        """إلغاء اشتراك"""
        for sub in self.subscriptions:
            if sub["id"] == sub_id:
                sub["status"] = "cancelled"
                self.save()
                return sub
        return None

    def get_active(self, category=None):
        """الاشتراكات النشطة"""
        active = [s for s in self.subscriptions
                  if s["status"] == "active"]
        if category:
            active = [s for s in active
                     if s.get("category") == category]
        return active

    def get_total_monthly(self):
        """المجموع الشهري"""
        total = 0
        for sub in self.subscriptions:
            if sub["status"] == "active":
                if sub["billing_cycle"] == "monthly":
                    total += sub["amount"]
                elif sub["billing_cycle"] == "yearly":
                    total += sub["amount"] / 12
        return total

    def check_reminders(self):
        """تحقق من تذكيرات الاشتراكات"""
        now = datetime.now()
        reminders = []
        reminder_days = SUB_REMINDER_DAYS

        for sub in self.subscriptions:
            if sub["status"] == "active" and sub.get("next_billing"):
                try:
                    next_date = datetime.fromisoformat(
                        sub["next_billing"]
                    )
                    days_left = (next_date - now).days
                    if 0 <= days_left <= reminder_days:
                        reminders.append({
                            **sub,
                            "days_left": days_left
                        })
                except (ValueError, TypeError):
                    continue

        return reminders

    def get_ns_links(self):
        """روابط NSsFOREX"""
        return NS_LINKS

    def get_all(self):
        """كل الاشتراكات"""
        return self.subscriptions

    def get_status(self):
        """حالة الاشتراكات"""
        active = len([s for s in self.subscriptions
                      if s["status"] == "active"])
        total = self.get_total_monthly()
        return f"✅ {active} نشط | المجموع الشهري: ${total:.2f}"
