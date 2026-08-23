# ============================================================
# Ghost Phone — هاتف الشبح
# مكالمات هاتفية
# ============================================================
import logging
from config import OWNER_NAME

logger = logging.getLogger(__name__)


class GhostPhone:
    """هاتف Ghost — بيتعامل مع المكالمات"""

    def __init__(self, memory=None, brain=None, voice=None):
        self.memory = memory
        self.brain = brain
        self.voice = voice

    async def handle_call(self, caller, duration=0):
        """معالجة مكالمة واردة"""
        # سجّل المكالمة
        if self.memory:
            self.memory.learn(
                f"call_{caller}",
                f"مكالمة من {caller} — المدة: {duration} ثانية",
                category="calls",
                source="phone"
            )

        # لو فيه صوت — رد صوتي
        if self.voice:
            greeting = "مرحباً! Ghost هون. كيف فيني ساعدك؟"
            audio = await self.voice.speak(greeting, lang="ar")
            return {"text": greeting, "audio": audio}

        return {"text": "مرحباً! Ghost هون. كيف فيني ساعدك؟"}

    def get_status(self):
        """حالة الهاتف"""
        return "✅ هاتف جاهز"
