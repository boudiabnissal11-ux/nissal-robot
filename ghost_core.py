# ============================================================
# Ghost Core — المرجع المركزي
# كل قناة (تيليجرام، لاحقاً واتساب وفيسبوك) تمر من هنا
# ============================================================

import logging
import ghost_db

logger = logging.getLogger(__name__)


class GhostCore:
    """العقل المركزي — نقطة القرار والتنفيذ الوحيدة"""

    def __init__(self, brain=None, personality=None, voice=None):
        self.brain = brain
        self.personality = personality
        self.voice = voice
        ghost_db.init_db()

    def decide_reply_language(self, response_type: str) -> str:
        """
        قرار لغة الرد — يعتمد فقط على نوع الرد المطلوب
        نص = فصحى دائماً | صوت أو مكالمة = لبناني دائماً
        """
        if response_type == "text":
            return "ar"
        elif response_type in ("voice", "call"):
            return "lb"
        return "ar"

    async def handle_incoming(
        self,
        platform: str,
        platform_user_id: str,
        sender_name: str,
        text: str,
        response_type: str = "text",
        is_owner: bool = False,
    ):
        """
        نقطة الدخول الموحدة لأي رسالة من أي قناة
        ترجع: (نص الرد, مسار ملف الصوت أو None)
        """
        lang = self.decide_reply_language(response_type)

        user = ghost_db.get_or_create_user(
            platform, platform_user_id, sender_name, is_owner
        )

        ghost_db.save_message(
            user_id=user["id"],
            platform=platform,
            sender=sender_name,
            message=text,
            response_type=response_type,
            lang=lang,
        )

        if is_owner and self.personality:
            self.personality.learn_style(text, source="owner")

        if self.brain:
            reply_text = await self.brain.think(
                user_message=text,
                lang=lang,
                sender_name=sender_name,
                platform=platform,
            )
        else:
            reply_text = "⚠️ العقل غير متصل"

        ghost_db.save_message(
            user_id=user["id"],
            platform=platform,
            sender="Ghost",
            message=reply_text,
            response_type=response_type,
            lang=lang,
        )

        voice_path = None
        if response_type in ("voice", "call") and self.voice:
            try:
                voice_path = await self.voice.speak(reply_text, lang=lang)
            except Exception as e:
                logger.error(f"فشل تحويل الرد لصوت: {e}")

        return reply_text, voice_path
