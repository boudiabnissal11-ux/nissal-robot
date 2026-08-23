# ============================================================
# Ghost Phone — هاتف الشبح
# مكالمات هاتفية عبر Twilio
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
    from twilio.twiml.voice_response import VoiceResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("⚠️ twilio مو مثبت")


class GhostPhone:
    """هاتف Ghost — مكالمات عبر Twilio"""

    def __init__(self, brain=None, memory=None, voice=None):
        self.brain = brain
        self.memory = memory
        self.voice = voice

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
                logger.info("✅ Twilio Phone جاهز")
            except Exception as e:
                logger.error(f"❌ خطأ Twilio Phone: {e}")

    def make_call(self, to_phone, message=None, voice_url=None):
        """إجراء مكالمة هاتفية"""
        if not self.client:
            logger.error("❌ Twilio مو جاهز")
            return False

        try:
            if voice_url:
                call = self.client.calls.create(
                    to=to_phone,
                    from_=self.phone_number,
                    url=voice_url
                )
            elif message:
                twiml = self._message_to_twiml(message)
                call = self.client.calls.create(
                    to=to_phone,
                    from_=self.phone_number,
                    twiml=twiml
                )
            else:
                logger.error("❌ لازم message أو voice_url")
                return False

            logger.info(f"📞 مكالمة لـ {to_phone} — SID: {call.sid}")
            return True

        except Exception as e:
            logger.error(f"❌ خطأ بالمكالمة: {e}")
            return False

    def _message_to_twiml(self, message, lang="ar"):
        """تحويل رسالة لـ TwiML صوتي"""
        response = VoiceResponse()
        voice = "alice" if lang == "en" else "Zeina"
        language = "en-US" if lang == "en" else "ar-SA"

        response.say(message, voice=voice, language=language)
        response.hangup()

        return str(response)

    def handle_incoming_call(self, from_phone):
        """معالجة مكالمة واردة"""
        greeting = (
            f"أهلاً، أنا Ghost، المساعد الشخصي لـ {OWNER_NAME}. "
            f"شكراً على اتصالك. سيتم إعلام المالك بمكالمتك."
        )
        twiml = self._message_to_twiml(greeting, lang="ar")

        # إعلام المالك
        if self.client:
            try:
                self.client.messages.create(
                    body=f"📞 مكالمة من {from_phone}",
                    from_=self.phone_number,
                    to=self.owner_phone
                )
            except Exception as e:
                logger.error(f"❌ خطأ إعلام المالك: {e}")

        return twiml

    def handle_gather_input(self, from_phone, digits=None,
                            speech=None):
        """معالجة إدخال المكالمة"""
        if speech and self.brain:
            response_text = self.brain.think(
                message=speech,
                sender_name=None,
                platform="phone",
                lang="ar"
            )
            twiml = self._message_to_twiml(response_text, lang="ar")
            return twiml

        if digits:
            if digits == "1":
                msg = (
                    f"للاشتراك بـ NSsFOREX، تفضل بزيارة: "
                    f"رابط تري-dot-اي-NSsFOREX"
                )
            elif digits == "2":
                msg = (
                    f"للتواصل مع {OWNER_NAME}: "
                    f"{NS_LINKS['owner']}"
                )
            else:
                msg = "خيار غير صحيح. شكراً على اتصالك."

            return self._message_to_twiml(msg, lang="ar")

        return self._message_to_twiml(
            "لم أفهم. شكراً على اتصالك.", lang="ar"
        )

    def send_sms(self, to_phone, message):
        """إرسال رسالة SMS"""
        if not self.client:
            logger.error("❌ Twilio مو جاهز")
            return False

        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone
            )
            logger.info(f"📱 SMS مرسل لـ {to_phone}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ SMS: {e}")
            return False

    def call_owner(self, message=None):
        """الاتصال بالمالك"""
        if self.owner_phone:
            return self.make_call(
                self.owner_phone, message=message
            )
        return False

    def send_owner_sms(self, message):
        """إرسال SMS للمالك"""
        if self.owner_phone:
            return self.send_sms(self.owner_phone, message)
        return False

    def get_call_history(self, limit=20):
        """سجل المكالمات"""
        if not self.client:
            return []

        try:
            calls = self.client.calls.list(limit=limit)
            history = []

            for call in calls:
                history.append({
                    "sid": call.sid,
                    "from": call.from_,
                    "to": call.to,
                    "status": call.status,
                    "duration": call.duration,
                    "date": str(call.date_created)
                })

            return history

        except Exception as e:
            logger.error(f"❌ خطأ سجل المكالمات: {e}")
            return []

    def get_status(self):
        """حالة الهاتف"""
        if not TWILIO_AVAILABLE:
            return "❌ Twilio مو مثبت"

        if not self.client:
            return "⚠️ Twilio ناقص مفاتيح"

        has_phone = bool(self.phone_number)
        if has_phone:
            return f"✅ هاتف جاهز — {self.phone_number}"
        else:
            return "⚠️ Twilio ناقص رقم هاتف"
