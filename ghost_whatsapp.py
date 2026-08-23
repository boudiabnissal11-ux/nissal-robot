# ============================================================
# Ghost WhatsApp — واتساب الشبح
# اتصال واتساب عبر Twilio
# ============================================================

import os
import logging
from datetime import datetime
from config import (
    OWNER_NAME, GHOST_NAME, OWNER_PHONE, NS_LINKS
)

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("⚠️ twilio مو مثبت")


class GhostWhatsApp:
    """واتساب Ghost — اتصال عبر Twilio"""

    def __init__(self, brain=None, memory=None, personality=None,
                 tasks=None, appointments=None, subscriptions=None,
                 pay=None):
        self.brain = brain
        self.memory = memory
        self.personality = personality
        self.tasks = tasks
        self.appointments = appointments
        self.subscriptions = subscriptions
        self.pay = pay

        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.phone_number = os.environ.get("TWILIO_PHONE_NUMBER", "")
        self.owner_phone = OWNER_PHONE
        self.client = None

        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.client = TwilioClient(
                    self.account_sid, self.auth_token
                )
                logger.info("✅ Twilio جاهز")
            except Exception as e:
                logger.error(f"❌ خطأ Twilio: {e}")

    def _is_owner(self, phone):
        """هل الرقم هو رقم المالك؟"""
        if not phone or not self.owner_phone:
            return False
        return phone.replace("+", "").replace(" ", "").replace(
            "-", ""
        ) == self.owner_phone.replace("+", "").replace(
            " ", ""
        ).replace("-", "")

    def send_message(self, to_phone, message):
        """إرسال رسالة واتساب"""
        if not self.client:
            logger.error("❌ Twilio مو جاهز")
            return False

        try:
            msg = self.client.messages.create(
                body=message,
                from_=f"whatsapp:{self.phone_number}",
                to=f"whatsapp:{to_phone}"
            )
            logger.info(f"💬 رسالة واتساب مرسلة لـ {to_phone}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ بإرسال واتساب: {e}")
            return False

    def handle_incoming(self, from_phone, message_body):
        """معالجة رسالة واردة"""
        is_owner = self._is_owner(from_phone)

        if self.brain:
            response = self.brain.think(
                message=message_body,
                sender_name=OWNER_NAME if is_owner else None,
                platform="whatsapp",
                lang=None
            )
        else:
            if is_owner:
                response = "👻 الدماغ مو جاهز بعد..."
            else:
                response = (
                    f"👻 شكراً لرسالتك! للاشتراك بـ NSsFOREX:\n"
                    f"📱 {NS_LINKS['telegram']}\n"
                    f"🌐 {NS_LINKS['linktree']}\n"
                    f"💬 {NS_LINKS['owner']}"
                )

        self.send_message(from_phone, response)
        return response

    def handle_start(self, from_phone):
        """رسالة بداية واتساب"""
        is_owner = self._is_owner(from_phone)

        if is_owner:
            msg = (
                f"👻 أهلا {OWNER_NAME}! أنا Ghost — شبحك الشخصي!\n\n"
                f"بقدر أساعدك بـ:\n"
                f"📋 المهام\n📅 المواعيد\n👥 الاشتراكات\n"
                f"💳 الدفعات\n🧠 الذواكر\n\n"
                f"أو بس حكيلي شو بدك! 👻"
            )
        else:
            msg = (
                f"👻 أهلا! أنا Ghost — بوت NSsFOREX!\n\n"
                f"للاشتراك والتفاصيل:\n"
                f"📱 {NS_LINKS['telegram']}\n"
                f"🌐 {NS_LINKS['linktree']}\n"
                f"💬 {NS_LINKS['owner']}"
            )

        self.send_message(from_phone, msg)
        return msg

    def send_reminder(self, to_phone, message):
        """إرسال تذكير واتساب"""
        return self.send_message(to_phone, f"⏰ {message}")

    def send_subscription_reminder(self, phone, reminder_msg):
        """إرسال تذكير اشتراك"""
        return self.send_message(phone, reminder_msg)

    def check_and_remind(self):
        """فحص وإرسال التذكيرات"""
        reminders_sent = []

        # تذكيرات المهام للمالك
        if self.tasks:
            task_reminders = self.tasks.get_reminders()
            for task in task_reminders:
                msg = f"⏰ تذكير مهمة: {task['title']}"
                if self.send_reminder(self.owner_phone, msg):
                    reminders_sent.append(("task", task["id"]))

        # تذكيرات المواعيد للمالك
        if self.appointments:
            apt_reminders = self.appointments.get_reminders()
            for apt in apt_reminders:
                msg = f"📅 موعد قريب: {apt['title']}"
                if self.send_reminder(self.owner_phone, msg):
                    reminders_sent.append(
                        ("appointment", apt["id"])
                    )

        # تذكيرات الاشتراكات
        if self.subscriptions:
            sub_reminders = self.subscriptions.get_reminders(
                lang="lb"
            )
            for reminder in sub_reminders:
                client_phone = reminder.get(
                    "subscription", {}
                ).get("client_id", "")
                platform = reminder.get(
                    "subscription", {}
                ).get("platform", "telegram")
                if platform == "whatsapp" and client_phone:
                    self.send_subscription_reminder(
                        client_phone, reminder["message"]
                    )
                    reminders_sent.append(
                        ("sub", reminder["subscription"]["id"])
                    )
                # نسخة للمالك
                client_name = reminder.get(
                    "subscription", {}
                ).get("client_name", "")
                owner_msg = f"📋 تذكير اشتراك: {client_name}"
                self.send_reminder(
                    self.owner_phone, owner_msg
                )

        return reminders_sent

    def format_webhook_response(self, message):
        """تنسيق رد الويبهوك"""
        return {"message": message}

    def get_status(self):
        """حالة واتساب"""
        if not TWILIO_AVAILABLE:
            return "❌ Twilio مو مثبت"

        if not self.client:
            return "⚠️ Twilio ناقص مفاتيح"

        has_phone = bool(self.phone_number)
        if has_phone:
            return f"✅ واتساب جاهز — {self.phone_number}"
        else:
            return "⚠️ Twilio ناقص رقم هاتف"
