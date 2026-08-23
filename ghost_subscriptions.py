# ============================================================
# Ghost Subscriptions — اشتراكات الشبح
# إدارة اشتراكات NSsFOREX والعملاء
# ============================================================

import os
import json
import logging
from datetime import datetime, timedelta
from config import (
    OWNER_NAME, GHOST_NAME, NS_LINKS, SUB_REMINDER_DAYS
)

logger = logging.getLogger(__name__)


class GhostSubscriptions:
    """اشتراكات Ghost — إدارة الاشتراكات"""

    def __init__(self, memory=None):
        self.memory = memory
        self.subs_file = os.environ.get(
            "SUBS_FILE", "data/subscriptions.json"
        )
        self.subscriptions = []
        self.reminder_days = SUB_REMINDER_DAYS
        self._load_subscriptions()

    def _load_subscriptions(self):
        """تحميل الاشتراكات من الملف"""
        try:
            os.makedirs(
                os.path.dirname(self.subs_file), exist_ok=True
            )
            if os.path.exists(self.subs_file):
                with open(self.subs_file, "r", encoding="utf-8") as f:
                    self.subscriptions = json.load(f)
                logger.info(
                    f"👥 تم تحميل {len(self.subscriptions)} اشتراك"
                )
            else:
                self.subscriptions = []
                self._save_subscriptions()
        except Exception as e:
            logger.error(f"❌ خطأ بتحميل الاشتراكات: {e}")
            self.subscriptions = []

    def _save_subscriptions(self):
        """حفظ الاشتراكات بالملف"""
        try:
            os.makedirs(
                os.path.dirname(self.subs_file), exist_ok=True
            )
            with open(self.subs_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.subscriptions, f,
                    ensure_ascii=False, indent=2
                )
            logger.info(
                f"👥 تم حفظ {len(self.subscriptions)} اشتراك"
            )
        except Exception as e:
            logger.error(f"❌ خطأ بحفظ الاشتراكات: {e}")

    def add_subscription(self, client_name, client_id,
                         plan="monthly", start_date=None,
                         end_date=None, amount=0,
                         currency="USD", platform="telegram",
                         notes=""):
        """إضافة اشتراك جديد"""
        if start_date is None:
            start_date = datetime.now().isoformat()
        if end_date is None:
            start = datetime.fromisoformat(start_date)
            if plan == "monthly":
                end = start + timedelta(days=30)
            elif plan == "quarterly":
                end = start + timedelta(days=90)
            elif plan == "yearly":
                end = start + timedelta(days=365)
            else:
                end = start + timedelta(days=30)
            end_date = end.isoformat()

        subscription = {
            "id": f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "client_name": client_name,
            "client_id": client_id,
            "plan": plan,
            "start_date": start_date,
            "end_date": end_date,
            "amount": amount,
            "currency": currency,
            "platform": platform,
            "notes": notes,
            "status": "active",
            "reminded": False,
            "created_at": datetime.now().isoformat()
        }

        self.subscriptions.append(subscription)
        self._save_subscriptions()

        logger.info(f"👥 اشتراك جديد: {client_name} — {plan}")
        return subscription

    def renew_subscription(self, sub_id, new_end_date=None,
                           plan=None):
        """تجديد اشتراك"""
        for sub in self.subscriptions:
            if sub["id"] == sub_id:
                if new_end_date:
                    sub["end_date"] = new_end_date
                elif plan:
                    start = datetime.fromisoformat(sub["end_date"])
                    if plan == "monthly":
                        end = start + timedelta(days=30)
                    elif plan == "quarterly":
                        end = start + timedelta(days=90)
                    elif plan == "yearly":
                        end = start + timedelta(days=365)
                    else:
                        end = start + timedelta(days=30)
                    sub["end_date"] = end.isoformat()
                    sub["plan"] = plan

                sub["status"] = "active"
                sub["reminded"] = False
                self._save_subscriptions()
                logger.info(f"🔄 اشتراك مُجدد: {sub['client_name']}")
                return sub

        logger.warning(f"⚠️ اشتراك غير موجود: {sub_id}")
        return None

    def cancel_subscription(self, sub_id):
        """إلغاء اشتراك"""
        for sub in self.subscriptions:
            if sub["id"] == sub_id:
                sub["status"] = "cancelled"
                self._save_subscriptions()
                logger.info(f"❌ اشتراك ملغى: {sub['client_name']}")
                return sub

        return None

    def get_expiring_soon(self, days=None):
        """الاشتراكات اللي راح تنتهي قريب"""
        if days is None:
            days = self.reminder_days

        now = datetime.now()
        threshold = now + timedelta(days=days)
        expiring = []

        for sub in self.subscriptions:
            if sub["status"] != "active":
                continue
            try:
                end_dt = datetime.fromisoformat(sub["end_date"])
                if now <= end_dt <= threshold:
                    expiring.append(sub)
            except (ValueError, TypeError):
                continue

        return expiring

    def get_expired(self):
        """الاشتراكات المنتهية"""
        now = datetime.now()
        expired = []

        for sub in self.subscriptions:
            if sub["status"] != "active":
                continue
            try:
                end_dt = datetime.fromisoformat(sub["end_date"])
                if end_dt < now:
                    sub["status"] = "expired"
                    expired.append(sub)
            except (ValueError, TypeError):
                continue

        if expired:
            self._save_subscriptions()

        return expired

    def get_reminders(self, lang="lb"):
        """تذكيرات الاشتراكات — مع روابط NSsFOREX"""
        reminders = []
        expiring = self.get_expiring_soon()

        for sub in expiring:
            if sub.get("reminded"):
                continue

            try:
                end_dt = datetime.fromisoformat(sub["end_date"])
                days_left = (end_dt - datetime.now()).days
            except (ValueError, TypeError):
                days_left = 0

            if lang == "lb":
                msg = (
                    f"⚠️ يا {sub['client_name']}، اشتراكك بـ NSsFOREX "
                    f"راح ينتهي بعد {days_left} يوم!\n\n"
                    f"🔄 جرّد الآن:\n"
                    f"📱 {NS_LINKS['telegram']}\n"
                    f"🌐 {NS_LINKS['linktree']}\n"
                    f"💬 {NS_LINKS['owner']}\n\n"
                    f"ما تفوّت الفرصة! 👻🔥"
                )
            elif lang == "ar":
                msg = (
                    f"⚠️ {sub['client_name']}، سينتهي اشتراكك في "
                    f"NSsFOREX خلال {days_left} يوم!\n\n"
                    f"🔄 اشترك الآن:\n"
                    f"📱 {NS_LINKS['telegram']}\n"
                    f"🌐 {NS_LINKS['linktree']}\n"
                    f"💬 {NS_LINKS['owner']}\n\n"
                    f"لا تفوت الفرصة! 👻🔥"
                )
            else:
                msg = (
                    f"⚠️ {sub['client_name']}, your NSsFOREX "
                    f"subscription expires in {days_left} days!\n\n"
                    f"🔄 Subscribe now:\n"
                    f"📱 {NS_LINKS['telegram']}\n"
                    f"🌐 {NS_LINKS['linktree']}\n"
                    f"💬 {NS_LINKS['owner']}\n\n"
                    f"Don't miss out! 👻🔥"
                )

            reminders.append({
                "subscription": sub,
                "message": msg,
                "client_id": sub["client_id"],
                "platform": sub["platform"]
            })
            sub["reminded"] = True

        if reminders:
            self._save_subscriptions()

        return reminders

    def format_subscriptions_list(self, subs=None, lang="lb"):
        """تنسيق قائمة الاشتراكات"""
        if subs is None:
            subs = [s for s in self.subscriptions
                    if s["status"] == "active"]

        if not subs:
            if lang == "lb":
                return "👥 ما في اشتراكات فعّالة حالياً 👻"
            elif lang == "ar":
                return "👥 لا توجد اشتراكات فعّالة حالياً 👻"
            else:
                return "👥 No active subscriptions 👻"

        lines = []
        if lang == "lb":
            lines.append("👥 اشتراكات NSsFOREX:")
        elif lang == "ar":
            lines.append("👥 اشتراكات NSsFOREX:")
        else:
            lines.append("👥 NSsFOREX Subscriptions:")

        status_emoji = {
            "active": "✅", "expired": "⏰",
            "cancelled": "❌"
        }

        for i, sub in enumerate(subs, 1):
            emoji = status_emoji.get(sub["status"], "⚪")
            try:
                end_dt = datetime.fromisoformat(sub["end_date"])
                end_str = end_dt.strftime("%m/%d/%Y")
                days_left = (end_dt - datetime.now()).days
                days_str = f" ({days_left}ي)"
            except (ValueError, TypeError):
                end_str = "—"
                days_str = ""

            lines.append(
                f"  {i}. {emoji} {sub['client_name']} — "
                f"{sub['plan']} | 📅 {end_str}{days_str}"
            )

        return "\n".join(lines)

    def get_subscriptions_summary(self, lang="lb"):
        """ملخص الاشتراكات"""
        active = len(
            [s for s in self.subscriptions if s["status"] == "active"]
        )
        expiring = len(self.get_expiring_soon())
        expired = len(
            [s for s in self.subscriptions if s["status"] == "expired"]
        )

        if lang == "lb":
            return (f"👥 {active} فعّال | ⏰ {expiring} قريب ينتهي | "
                    f"❌ {expired} منتهي")
        elif lang == "ar":
            return (f"👥 {active} فعّال | ⏰ {expiring} قريب ينتهي | "
                    f"❌ {expired} منتهي")
        else:
            return (f"👥 {active} active | ⏰ {expiring} expiring | "
                    f"❌ {expired} expired")
