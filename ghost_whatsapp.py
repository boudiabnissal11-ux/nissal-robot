# ============================================================
# Ghost WhatsApp — واتساب الشبح
# جسر واتساب → تيليجرام
# ============================================================

import os
import logging
from datetime import datetime
from config import (
    OWNER_NAME, GHOST_NAME, OWNER_PHONE,
    NS_LINKS, SUB_REMINDER_DAYS
)

logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("⚠️ twilio مو مثبت")


class GhostWhatsApp:
    """واتساب Ghost — جسر واتساب→تيليجرام"""

    def __init__(self, brain=None, memory=None,
                 tasks=None, appointments=None,
                 subscriptions=None, telegram=None):
        self.brain = brain
        self.memory = memory
        self.tasks = tasks
        self.appointments = appointments
        self.subscriptions = subscriptions
        self.telegram = telegram  # جسر لتيليجرام

        self.account_sid = os.environ.get(
            "TWILIO_ACCOUNT_SID", ""
        )
        self.auth_token = os.environ.get(
            "TWILIO_AUTH_TOKEN", ""
        )
        self.phone_number = os.environ.get(
            "TWILIO_PHONE_NUMBER", ""
        )
        self.owner_phone = OWNER_PHONE
        self.client = None

        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.client = TwilioClient(
                    self.account_sid, self.auth_token
                )
                logger.info("✅ Twilio WhatsApp جاهز")
            except Exception as e:
                logger.error(f"❌ خطأ Twilio WhatsApp: {e}")

    # ========================================================
    # استقبال رسائل واتساب
    # ========================================================

    def handle_incoming(self, from_phone, message,
                        profile_name=None):
        """معالجة رسالة واتساب واردة — تحويل لتيليجرام"""
        logger.info(
            f"💬 واتساب من {from_phone}: {message}"
        )

        # حفظ بالذاكرة
        if self.memory:
            self.memory.save_message(
                sender=from_phone,
                message=message,
                platform="whatsapp",
                is_owner=False
            )

        # --- الجسر: تحويل لتيليجرام ---
        if self.telegram:
            # استخدام async بحدث لاحق
            self._pending_whatsapp = {
                "phone": from_phone,
                "message": message,
                "name": profile_name or from_phone
            }
            logger.info(
                "📩 رسالة واتساب جاهزة للتحويل لتيليجرام"
            )
            return self._format_for_telegram(
                from_phone, message, profile_name
            )

        # بدون جسر — رد مباشر على واتساب
        if self.brain:
            response = self.brain.think(
                message=message,
                sender_name=profile_name or from_phone,
                platform="whatsapp",
                lang="ar"
            )
            return response

        return "👻 Ghost هنا"

    def _format_for_telegram(self, from_phone, message,
                             profile_name=None):
        """تنسيق رسالة واتساب لتيليجرام"""
        name = profile_name or from_phone
        text = (
            f"💬 رسالة واتساب جديدة!\n\n"
            f"📞 من: {name}\n"
            f"📱 رقم: {from_phone}\n"
            f"📝 الرسالة: {message}\n\n"
        )

        # يلقي رد Ghost
        if self.brain:
            response = self.brain.think(
                message=message,
                sender_name=name,
                platform="whatsapp",
                lang="ar"
            )
            text += f"👻 رد Ghost:\n{response}"

        return text

    # ========================================================
    # إرسال رسائل واتساب
    # ========================================================

    def send_message(self, to_phone, message):
        """إرسال رسالة واتساب عبر Twilio"""
        if not self.client:
            logger.error("❌ Twilio WhatsApp مو جاهز")
            return False

        try:
            msg = self.client.messages.create(
                body=message,
                from_=f"whatsapp:{self.phone_number}",
                to=f"whatsapp:{to_phone}"
            )
            logger.info(
                f"💬 واتساب مرسل لـ {to_phone}"
            )
            return True
        except Exception as e:
            logger.error(
                f"❌ خطأ إرسال واتساب: {e}"
            )
            return False

    def send_owner_whatsapp(self, message):
        """إرسال واتساب للمالك"""
        if self.owner_phone:
            return self.send_message(
                self.owner_phone, message
            )
        return False

    # ========================================================
    # أوامر واتساب
    # ========================================================

    def handle_command(self, from_phone, command):
        """معالجة أوامر واتساب"""
        cmd = command.strip().lower()

        if cmd in ["/start", "/بدء"]:
            return (
                f"أهلاً! أنا {GHOST_NAME}، "
                f"المساعد الشخصي لـ {OWNER_NAME} 👻"
            )

        elif cmd in ["/help", "/مساعدة"]:
            return (
                "👻 أوامر واتساب:\n\n"
                "/بدء — ترحيب\n"
                "/اشتراك — معلومات NSsFOREX\n"
                "/تواصل — التواصل مع المالك\n"
                "أو ارسل أي رسالة!"
            )

        elif cmd in ["/nss", "/اشتراك"]:
            return (
                f"📈 NSsFOREX — اشتراك!\n\n"
                f"تيليجرام: {NS_LINKS['telegram']}\n"
                f"Linktree: {NS_LINKS['linktree']}\n"
                f"نيسال: {NS_LINKS['owner']}"
            )

        elif cmd in ["/contact", "/تواصل"]:
            return (
                f"📞 تواصل مع {OWNER_NAME}:\n"
                f"تيليجرام: {NS_LINKS['owner']}"
            )

        return None

    # ========================================================
    # تذكير الاشتراكات
    # ========================================================

    def send_subscription_reminder(self, to_phone, sub_name,
                                    days_left, price=""):
        """إرسال تذكير اشتراك على واتساب"""
        text = (
            f"⏰ تذكير اشتراك!\n\n"
            f"📋 {sub_name}\n"
            f"📅 باقي {days_left} يوم\n"
        )
        if price:
            text += f"💰 السعر: {price}\n"

        text += (
            f"\n📈 جدّد عبر NSsFOREX:\n"
            f"{NS_LINKS['linktree']}\n"
            f"{NS_LINKS['telegram']}\n"
            f"{NS_LINKS['owner']}"
        )

        return self.send_message(to_phone, text)

    # ========================================================
    # الحالة
    # ========================================================

    def get_status(self):
        """حالة واتساب"""
        if not TWILIO_AVAILABLE:
            return "❌ Twilio مو مثبت"

        if not self.client:
            return "⚠️ Twilio WhatsApp ناقص مفاتيح"

        has_bridge = "✅" if self.telegram else "❌"
        return (
            f"✅ واتساب جاهز — "
            f"جسر تيليجرام: {has_bridge}"
        )
