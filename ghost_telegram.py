# ============================================================
# Ghost Telegram — تيليجرام الشبح
# البوت اللي بيتواصل مع الناس
# ============================================================
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_TELEGRAM_ID, OWNER_NAME

logger = logging.getLogger(__name__)


class GhostTelegram:
    """تيليجرام Ghost — بيتواصل مع الناس"""

    def __init__(self, memory=None, brain=None, personality=None, voice=None,
                 tasks=None, appointments=None, subscriptions=None, pay=None):
        self.memory = memory
        self.brain = brain
        self.personality = personality
        self.voice = voice
        self.tasks = tasks
        self.appointments = appointments
        self.subscriptions = subscriptions
        self.pay = pay

    async def handle_message(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل الواردة"""
        user = update.effective_user
        message = update.effective_message
        text = message.text if message and message.text else ""

        if not text:
            return

        # تحقق من المالك
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        # كشف اللغة
        lang = self.personality.detect_language(text) if self.personality else "lb"

        # احفظ الرسالة
        sender_name = user.first_name or ""
        if self.memory:
            self.memory.save_message(
                sender=sender_name,
                message=text,
                platform="telegram",
                is_owner=is_owner
            )

        # لو المالك حكى
        if is_owner:
            # تعلّم أسلوبه
            if self.personality:
                self.personality.learn_style(text, source="owner")

            # رد من العقل
            if self.brain:
                reply = await self.brain.think(
                    user_message=text,
                    lang=lang,
                    sender_name=OWNER_NAME,
                    platform="telegram"
                )
            else:
                reply = "⚠️ العقل مو شغال!"
        else:
            # شخص غريب — رد محترم بس ما تعطي معلومات
            if self.brain:
                reply = await self.brain.think(
                    user_message=text,
                    lang=lang,
                    sender_name=sender_name,
                    platform="telegram"
                )
            else:
                reply = "⚠️ Ghost مو شغال حالياً"

        # أرسل الرد
        if message:
            await message.reply_text(reply)

        # احفظ رد Ghost
        if self.memory:
            self.memory.save_message(
                sender="Ghost",
                message=reply,
                platform="telegram",
                is_ghost=True
            )

    async def handle_start(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        """أمر /start"""
        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if is_owner:
            greeting = self.personality.get_greeting("lb") if self.personality else "أهلاً!"
            await update.message.reply_text(
                f"{greeting}\n\n"
                f"أنا Ghost — الشبح 👻\n"
                f"مساعدك الشخصي يا {OWNER_NAME}!\n\n"
                f"شغّلني بأمر: /شغل\n"
                f"وقّفني بأمر: /وقف"
            )
        else:
            await update.message.reply_text(
                "أهلاً! 👻 أنا Ghost — مساعد شخصي.\n"
                "كيف فيني ساعدك؟"
            )

    async def handle_activate(self, update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
        """أمر /شغل — تفعيل Ghost"""
        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if not is_owner:
            await update.message.reply_text("⛔ هاد الأمر للمالك فقط!")
            return

        context.bot_data["ghost_active"] = True
        greeting = self.personality.get_greeting("lb") if self.personality else "شبح مفعّل!"
        await update.message.reply_text(
            f"{greeting}\n\n"
            f"✅ Ghost شغال يا {OWNER_NAME}! 👻"
        )

    async def handle_deactivate(self, update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
        """أمر /وقف — إيقاف Ghost"""
        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if not is_owner:
            await update.message.reply_text("⛔ هاد الأمر للمالك فقط!")
            return

        context.bot_data["ghost_active"] = False
        farewell = self.personality.get_farewell("lb") if self.personality else "مع السلامة!"
        await update.message.reply_text(
            f"{farewell}\n\n"
            f"🔴 Ghost وقّف يا {OWNER_NAME}."
        )

    def get_status(self):
        """حالة تيليجرام"""
        return "✅ تيليجرام جاهز"
