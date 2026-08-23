# ============================================================
# Ghost Pay — دفعات الشبح
# تتبع الدفعات والفواتير
# ============================================================

import os
import json
import logging
from datetime import datetime, timedelta
from config import OWNER_NAME, GHOST_NAME

logger = logging.getLogger(__name__)


class GhostPay:
    """دفعات Ghost — تتبع الدفعات"""

    def __init__(self, memory=None):
        self.memory = memory
        self.payments_file = os.environ.get(
            "PAYMENTS_FILE", "data/payments.json"
        )
        self.payments = []
        self._load_payments()

    def _load_payments(self):
        """تحميل الدفعات من الملف"""
        try:
            os.makedirs(
                os.path.dirname(self.payments_file), exist_ok=True
            )
            if os.path.exists(self.payments_file):
                with open(self.payments_file, "r",
                          encoding="utf-8") as f:
                    self.payments = json.load(f)
                logger.info(
                    f"💳 تم تحميل {len(self.payments)} دفعة"
                )
            else:
                self.payments = []
                self._save_payments()
        except Exception as e:
            logger.error(f"❌ خطأ بتحميل الدفعات: {e}")
            self.payments = []

    def _save_payments(self):
        """حفظ الدفعات بالملف"""
        try:
            os.makedirs(
                os.path.dirname(self.payments_file), exist_ok=True
            )
            with open(self.payments_file, "w",
                      encoding="utf-8") as f:
                json.dump(
                    self.payments, f,
                    ensure_ascii=False, indent=2
                )
            logger.info(
                f"💳 تم حفظ {len(self.payments)} دفعة"
            )
        except Exception as e:
            logger.error(f"❌ خطأ بحفظ الدفعات: {e}")

    def add_payment(self, title, amount, currency="USD",
                    category="subscription", client_name=None,
                    due_date=None, status="pending",
                    payment_method="", notes=""):
        """إضافة دفعة جديدة"""
        payment = {
            "id": f"pay_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "amount": float(amount),
            "currency": currency,
            "category": category,
            "client_name": client_name or "",
            "due_date": due_date,
            "status": status,
            "payment_method": payment_method,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "paid_at": None
        }

        self.payments.append(payment)
        self._save_payments()

        logger.info(f"💳 دفعة جديدة: {title} — {amount} {currency}")
        return payment

    def mark_paid(self, payment_id, payment_method=""):
        """تحديد دفعة كمدفوعة"""
        for pay in self.payments:
            if pay["id"] == payment_id:
                pay["status"] = "paid"
                pay["paid_at"] = datetime.now().isoformat()
                if payment_method:
                    pay["payment_method"] = payment_method
                self._save_payments()
                logger.info(f"✅ دفعة مدفوعة: {pay['title']}")
                return pay

        logger.warning(f"⚠️ دفعة غير موجودة: {payment_id}")
        return None

    def mark_unpaid(self, payment_id):
        """تحديد دفعة كغير مدفوعة"""
        for pay in self.payments:
            if pay["id"] == payment_id:
                pay["status"] = "unpaid"
                self._save_payments()
                logger.info(f"❌ دفعة غير مدفوعة: {pay['title']}")
                return pay

        return None

    def get_pending_payments(self):
        """الدفعات المعلّقة"""
        return [p for p in self.payments
                if p["status"] in ("pending", "unpaid")]

    def get_overdue_payments(self):
        """الدفعات المتأخرة"""
        now = datetime.now().isoformat()
        overdue = []

        for pay in self.payments:
            if pay["status"] not in ("pending", "unpaid"):
                continue
            if pay.get("due_date") and pay["due_date"] < now:
                overdue.append(pay)

        return overdue

    def get_payments_by_client(self, client_name):
        """دفعات عميل معيّن"""
        return [p for p in self.payments
                if p.get("client_name", "").lower()
                == client_name.lower()]

    def get_revenue_summary(self, period="month"):
        """ملخص الإيرادات"""
        now = datetime.now()

        if period == "today":
            start = now.replace(hour=0, minute=0, second=0)
        elif period == "week":
            start = now - timedelta(days=7)
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0)
        elif period == "year":
            start = now.replace(month=1, day=1,
                                hour=0, minute=0, second=0)
        else:
            start = now - timedelta(days=30)

        total_paid = 0
        total_pending = 0
        total_overdue = 0
        currency = "USD"

        for pay in self.payments:
            try:
                created = datetime.fromisoformat(
                    pay["created_at"]
                )
                if created >= start:
                    if pay["status"] == "paid":
                        total_paid += pay["amount"]
                    elif pay["status"] in ("pending", "unpaid"):
                        if (pay.get("due_date")
                                and pay["due_date"]
                                < now.isoformat()):
                            total_overdue += pay["amount"]
                        else:
                            total_pending += pay["amount"]
            except (ValueError, TypeError):
                continue

        return {
            "period": period,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "total_overdue": total_overdue,
            "currency": currency
        }

    def format_payment(self, payment, lang="lb"):
        """تنسيق دفعة واحدة"""
        status_emoji = {
            "paid": "✅", "pending": "⏳",
            "unpaid": "❌", "overdue": "⚠️"
        }
        emoji = status_emoji.get(payment["status"], "⚪")

        amount_str = f"{payment['amount']:.2f} {payment['currency']}"
        due = ""
        if payment.get("due_date"):
            try:
                dt = datetime.fromisoformat(payment["due_date"])
                due = f" — 📅 {dt.strftime('%m/%d/%Y')}"
            except (ValueError, TypeError):
                due = ""

        client = ""
        if payment.get("client_name"):
            client = f" | 👤 {payment['client_name']}"

        return (
            f"{emoji} {payment['title']} — "
            f"💰 {amount_str}{due}{client}"
        )

    def format_payments_list(self, payments=None, lang="lb"):
        """تنسيق قائمة الدفعات"""
        if payments is None:
            payments = self.get_pending_payments()

        if not payments:
            if lang == "lb":
                return "💳 ما في دفعات معلّقة — كل شي مدفوع! 👻"
            elif lang == "ar":
                return "💳 لا توجد دفعات معلقة — كل شيء مدفوع! 👻"
            else:
                return "💳 No pending payments — all clear! 👻"

        lines = []
        if lang == "lb":
            lines.append(f"💳 دفعاتك يا {OWNER_NAME}:")
        elif lang == "ar":
            lines.append(f"💳 دفعاتك يا {OWNER_NAME}:")
        else:
            lines.append(f"💳 Payments for {OWNER_NAME}:")

        for i, pay in enumerate(payments, 1):
            lines.append(f"  {i}. {self.format_payment(pay, lang)}")

        return "\n".join(lines)

    def get_pay_summary(self, lang="lb", period="month"):
        """ملخص الدفعات"""
        summary = self.get_revenue_summary(period)

        if lang == "lb":
            return (f"💰 المدفوع: ${summary['total_paid']:.2f} | "
                    f"⏳ المعلّق: ${summary['total_pending']:.2f} | "
                    f"⚠️ المتأخر: ${summary['total_overdue']:.2f}")
        elif lang == "ar":
            return (f"💰 المدفوع: ${summary['total_paid']:.2f} | "
                    f"⏳ المعلق: ${summary['total_pending']:.2f} | "
                    f"⚠️ المتأخر: ${summary['total_overdue']:.2f}")
        else:
            return (f"💰 Paid: ${summary['total_paid']:.2f} | "
                    f"⏳ Pending: ${summary['total_pending']:.2f} | "
                    f"⚠️ Overdue: ${summary['total_overdue']:.2f}")
