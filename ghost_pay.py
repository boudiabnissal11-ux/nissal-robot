# ============================================================
# Ghost Pay — دفع الشبح
# إدارة المدفوعات
# ============================================================
import json
import os
from datetime import datetime
from config import OWNER_NAME, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET


class GhostPay:
    """دفع Ghost — بيعمل حساب لنصال"""

    def __init__(self, memory=None, brain=None):
        self.memory = memory
        self.brain = brain
        self.payments_file = "data/payments.json"
        self.stripe_key = STRIPE_SECRET_KEY
        self.stripe_webhook = STRIPE_WEBHOOK_SECRET
        self.payments = []
        self.load()

    def load(self):
        """تحميل المدفوعات"""
        if os.path.exists(self.payments_file):
            try:
                with open(self.payments_file, "r", encoding="utf-8") as f:
                    self.payments = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.payments = []
        else:
            os.makedirs(os.path.dirname(self.payments_file), exist_ok=True)
            self.payments = []

    def save(self):
        """حفظ المدفوعات"""
        os.makedirs(os.path.dirname(self.payments_file), exist_ok=True)
        with open(self.payments_file, "w", encoding="utf-8") as f:
            json.dump(self.payments, f, ensure_ascii=False, indent=2)

    def record_payment(self, title, amount, currency="USD",
                       status="completed", category="general",
                       notes=""):
        """تسجيل دفعة"""
        payment = {
            "id": len(self.payments) + 1,
            "title": title,
            "amount": amount,
            "currency": currency,
            "status": status,
            "category": category,
            "notes": notes,
            "created_at": str(datetime.now()),
        }
        self.payments.append(payment)
        self.save()

        # علّم الذاكرة
        if self.memory:
            self.memory.learn(
                f"payment_{payment['id']}",
                f"{title} — {amount} {currency}",
                category="payments",
                source="owner"
            )

        return payment

    def get_total(self, category=None, start_date=None, end_date=None):
        """المجموع"""
        total = 0
        for p in self.payments:
            if p["status"] == "completed":
                if category and p.get("category") != category:
                    continue
                if start_date or end_date:
                    try:
                        p_date = datetime.fromisoformat(p["created_at"])
                        if start_date and p_date < datetime.fromisoformat(start_date):
                            continue
                        if end_date and p_date > datetime.fromisoformat(end_date):
                            continue
                    except (ValueError, TypeError):
                        continue
                total += p["amount"]
        return total

    def get_all(self):
        """كل المدفوعات"""
        return self.payments

    def get_status(self):
        """حالة المدفوعات"""
        total = self.get_total()
        return f"✅ {len(self.payments)} دفعة | المجموع: ${total:.2f}"
