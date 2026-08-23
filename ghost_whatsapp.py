# ============================================================
# Ghost WhatsApp — واتساب الشبح
# جسر واتساب ↔ تيليجرام
# ============================================================
import logging
from config import OWNER_NAME, OWNER_TELEGRAM_ID

logger = logging.getLogger(__name__)


class GhostWhatsApp:
    """واتساب Ghost — بيحوّل الرسائل بين واتساب وتيليجرام"""

    def __init__(self, telegram=None, memory=None, brain=None):
        self.telegram = telegram
        self.memory = memory
        self.brain = brain

    async def handle_incoming(self, sender, message, from_number=None):
        """معالجة رسالة واتساب واردة"""
        # احفظ الرسالة
        if self.memory:
            self.memory.save_message(
                sender=sender,
                message=message,
                platform="whatsapp",
                is_owner=False
            )

        # لو فيه جسر تيليجرام —حوّل الرسالة
        if self.telegram:
            forward_msg = (
                f"📱 واتساب من {sender}:\n"
                f"{message}"
            )
            # إرسال لنصال على تيليجرام
            try:
                await self.telegram.forward_to_owner(forward_msg)
            except Exception as e:
                logger.error(f"خطأ بتحويل رسالة واتساب: {e}")

        # رد تلقائي
        if self.brain:
            reply = await self.brain.think(
                user_message=message,
                lang="ar",
                sender_name=sender,
                platform="whatsapp"
            )
            return reply

        return "شكراً لتواصلك! Ghost رح يرد عليك قريباً."

    async def forward_to_owner(self, message):
        """تحويل رسالة لنصال على واتساب"""
        # بيحتاج تويليو
        logger.info(f"تحويل لنصال على واتساب: {message[:50]}")
        return True

    def get_status(self):
        """حالة واتساب"""
        has_telegram = "✅" if self.telegram else "❌"
        return f"{has_telegram} جسر تيليجرام | واتساب: جاهز"
