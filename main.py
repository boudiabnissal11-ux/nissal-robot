# ============================================================
# Ghost — الشبح
# المساعد الشخصي الذكي لنيسال
# الملف الرئيسي للتشغيل
# ============================================================

import os
import sys
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# تحميل .env
load_dotenv()

# ============================================================
# إعداد السجلات
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ghost.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("Ghost")

# ============================================================
# تحميل الإعدادات
# ============================================================
from config import (
    OWNER_NAME, OWNER_TELEGRAM_ID, OWNER_PHONE,
    GHOST_NAME, GITHUB_REPO_URL,
    LLM_PROVIDER, LLM_MODEL, LLM_API_KEY,
    TELEGRAM_BOT_TOKEN, TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,
    NS_LINKS, SUB_REMINDER_DAYS
)

# ============================================================
# تحميل وحدات Ghost
# ============================================================
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


# ============================================================
# كلاس Ghost الرئيسي
# ============================================================
class Ghost:
    """الشبح — المساعد الشخصي لنيسال"""

    def __init__(self):
        logger.info(f"👻 {GHOST_NAME} يبدأ التحميل...")

        # --- الذاكرة ---
        self.memory = GhostMemory()
        logger.info("✅ الذاكرة جاهزة")

        # --- الشخصية ---
        self.personality = GhostPersonality()
        logger.info("✅ الشخصية جاهزة")

        # --- العقل ---
        self.brain = GhostBrain(
            memory=self.memory,
            personality=self.personality
        )
        logger.info("✅ العقل جاهز")

        # --- الصوت ---
        self.voice = GhostVoice()
        logger.info("✅ الصوت جاهز")

        # --- المهام ---
        self.tasks = GhostTasks(
            memory=self.memory,
            brain=self.brain
        )
        logger.info("✅ المهام جاهزة")

        # --- المواعيد ---
        self.appointments = GhostAppointments(
            memory=self.memory,
            brain=self.brain
        )
        logger.info("✅ المواعيد جاهزة")

        # --- الاشتراكات ---
        self.subscriptions = GhostSubscriptions(
            memory=self.memory,
            brain=self.brain
        )
        logger.info("✅ الاشتراكات جاهزة")

        # --- الدفع ---
        self.pay = GhostPay(
            memory=self.memory,
            brain=self.brain
        )
        logger.info("✅ الدفع جاهز")

        # --- تيليجرام ---
        self.telegram = GhostTelegram(
            brain=self.brain,
            memory=self.memory,
            tasks=self.tasks,
            appointments=self.appointments,
            subscriptions=self.subscriptions,
            pay=self.pay
        )
        logger.info("✅ تيليجرام جاهز")

        # --- واتساب ---
        self.whatsapp = GhostWhatsApp(
            brain=self.brain,
            memory=self.memory,
            tasks=self.tasks,
            appointments=self.appointments,
            subscriptions=self.subscriptions
        )
        logger.info("✅ واتساب جاهز")

        # --- الهاتف ---
        self.phone = GhostPhone(
            brain=self.brain,
            memory=self.memory,
            voice=self.voice
        )
        logger.info("✅ الهاتف جاهز")

        # --- ملخص الحالة ---
        self._print_status()
        logger.info(f"👻 {GHOST_NAME} جاهز بالكامل!")

    def _print_status(self):
        """طباعة حالة كل وحدة"""
        logger.info("=" * 50)
        logger.info(f"👻 {GHOST_NAME} — تقرير الحالة")
        logger.info("=" * 50)

        modules = {
            "الذاكرة": self.memory,
            "العقل": self.brain,
            "المهام": self.tasks,
            "المواعيد": self.appointments,
            "الاشتراكات": self.subscriptions,
            "الدفع": self.pay,
            "تيليجرام": self.telegram,
            "واتساب": self.whatsapp,
            "الهاتف": self.phone
        }

        for name, module in modules.items():
            if hasattr(module, "get_status"):
                status = module.get_status()
            else:
                status = "✅ جاهز"
            logger.info(f"  {name}: {status}")

        logger.info("=" * 50)

    async def run(self):
        """تشغيل Ghost"""
        logger.info("🚀 Ghost يبدأ التشغيل...")

        # فحص المفاتيح المطلوبة
        self._check_required_keys()

        # تشغيل تيليجرام (المنصة الأساسية)
        if TELEGRAM_BOT_TOKEN:
            logger.info("📱 بدء تشغيل تيليجرام...")
            await self.telegram.start()
        else:
            logger.warning(
                "⚠️ TELEGRAM_BOT_TOKEN ناقص — "
                "تيليجرام لن يعمل"
            )

    def _check_required_keys(self):
        """فحص المفاتيح المطلوبة"""
        missing = []

        if not TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not LLM_API_KEY:
            missing.append("LLM_API_KEY")

        if missing:
            logger.warning(
                f"⚠️ مفاتيح ناقصة: {', '.join(missing)}"
            )
            logger.warning(
                "⚠️ بعض الوظائف لن تعمل بدون هذه المفاتيح"
            )
        else:
            logger.info("✅ جميع المفاتيح الأساسية موجودة")


# ============================================================
# نقطة البداية
# ============================================================
def main():
    """تشغيل Ghost"""
    print(f"""
    ╔══════════════════════════════════════╗
    ║          👻 GHOST — الشبح 👻         ║
    ║     المساعد الشخصي لنيسال           ║
    ║                                      ║
    ║  GitHub: {GITHUB_REPO_URL[:28]:<28s}  ║
    ╚══════════════════════════════════════╝
    """)

    ghost = Ghost()

    try:
        asyncio.run(ghost.run())
    except KeyboardInterrupt:
        logger.info("👋 Ghost تم إيقافه")
    except Exception as e:
        logger.error(f"❌ خطأ رئيسي: {e}")
        raise


if __name__ == "__main__":
    main()
