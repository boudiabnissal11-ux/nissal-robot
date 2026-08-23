# ============================================================
# Ghost — الشبح
# المساعد الشخصي لنصال
# ============================================================
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN, OWNER_NAME, OWNER_TELEGRAM_ID
from ghost_memory import GhostMemory
from ghost_personality import GhostPersonality
from ghost_brain import GhostBrain
from ghost_voice import GhostVoice
from ghost_tasks import GhostTasks
from ghost_appointments import GhostAppointments
from ghost_subscriptions import GhostSubscriptions
from ghost_pay import GhostPay
from ghost_telegram import GhostTelegram
from ghost_whatsapp import GhostWhatsApp
from ghost_phone import GhostPhone

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class Ghost:
    """Ghost — الشبح 👻 المساعد الشخصي لنصال"""

    def __init__(self):
        logger.info("👻 Ghost بيستيقظ...")

        # === نواة Ghost ===
        self.memory = GhostMemory()
        self.personality = GhostPersonality()

        # العقل — الآن بيقبل memory و personality بالconstructor
        self.brain = GhostBrain(
            memory=self.memory,
            personality=self.personality
        )

        # === الصوت ===
        self.voice = GhostVoice()

        # === المهام ===
        self.tasks = GhostTasks(
            memory=self.memory,
            brain=self.brain
        )

        # === المواعيد ===
        self.appointments = GhostAppointments(
            memory=self.memory,
            brain=self.brain
        )

        # === الاشتراكات ===
        self.subscriptions = GhostSubscriptions(
            memory=self.memory,
            brain=self.brain
        )

        # === المدفوعات ===
        self.pay = GhostPay(
            memory=self.memory,
            brain=self.brain
        )

        # === تيليجرام ===
        self.telegram = GhostTelegram(
            memory=self.memory,
            brain=self.brain,
            personality=self.personality,
            voice=self.voice,
            tasks=self.tasks,
            appointments=self.appointments,
            subscriptions=self.subscriptions,
            pay=self.pay
        )

        # === واتساب — ممرّر telegram=self.telegram ===
        self.whatsapp = GhostWhatsApp(
            telegram=self.telegram,
            memory=self.memory,
            brain=self.brain
        )

        # === هاتف ===
        self.phone = GhostPhone(
            memory=self.memory,
            brain=self.brain,
            voice=self.voice
        )

        logger.info("✅ Ghost جاهز!")

    async def post_init(self, application):
        """بعد بدء البوت"""
        logger.info(f"👻 Ghost شغال! المالك: {OWNER_NAME}")
        logger.info(f"📊 الذاكرة: {self.memory.get_status()}")
        logger.info(f"🧠 العقل: {self.brain.get_status()}")

    def run(self):
        """تشغيل Ghost"""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ TELEGRAM_BOT_TOKEN مو موجود!")
            return

        # بناء التطبيق
        app = (
            ApplicationBuilder()
            .token(TELEGRAM_BOT_TOKEN)
            .post_init(self.post_init)
            .build()
        )

        # أوامر المالك
        app.add_handler(CommandHandler("start", self.telegram.handle_start))
        app.add_handler(CommandHandler("شغل", self.telegram.handle_activate))
        app.add_handler(CommandHandler("وقف", self.telegram.handle_deactivate))

        # الرسائل
        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.telegram.handle_message
            )
        )

        logger.info("🚀 Ghost بيشتغل...")
        app.run_polling()


def main():
    """نقطة البداية"""
    ghost = Ghost()
    ghost.run()


if __name__ == "__main__":
    main()
