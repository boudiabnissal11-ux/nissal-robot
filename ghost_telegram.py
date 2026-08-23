# ============================================================
# Ghost Telegram — تيليجرام الشبح
# بوت تيليجرام مع مفتاح تشغيل/إيقاف
# ============================================================

import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from config import (
    OWNER_NAME, GHOST_NAME, OWNER_TELEGRAM_ID,
    TELEGRAM_BOT_TOKEN, NS_LINKS, SUB_REMINDER_DAYS
)

logger = logging.getLogger(__name__)


class GhostTelegram:
    """تيليجرام Ghost — بوت مع مفتاح تشغيل/إيقاف"""

    def __init__(self, brain=None, memory=None,
                 tasks=None, appointments=None,
                 subscriptions=None, pay=None):
        self.brain = brain
        self.memory = memory
        self.tasks = tasks
        self.appointments = appointments
        self.subscriptions = subscriptions
        self.pay = pay

        self.token = TELEGRAM_BOT_TOKEN
        self.app = None

        # --- مفتاح التشغيل/الإيقاف ---
        self.ghost_active = True

        # --- رسالة الإيقاف ---
        self.off_message = (
            "👻 الشبح نايم حالياً 😴\n"
            "رجع بعدين وقت ما يكون مستيقظ!"
        )

        logger.info("✅ GhostTelegram جاهز")

    # ========================================================
    # مفتاح التشغيل والإيقاف (المالك فقط)
    # ========================================================

    async def cmd_ghost_on(self, update, context):
        """تشغيل Ghost — المالك فقط"""
        user_id = str(update.effective_user.id)
        if user_id != str(OWNER_TELEGRAM_ID):
            await update.message.reply_text(
                "❌ مو أنت المالك! ما تقدر تشغل الشبح."
            )
            return

        self.ghost_active = True
        await update.message.reply_text(
            "👻 Ghost شغال! ✅\n"
            "أنا فاضي لخدمتك يا حبيبي!"
        )
        logger.info("✅ Ghost تم تشغيله")

    async def cmd_ghost_off(self, update, context):
        """إيقاف Ghost — المالك فقط"""
        user_id = str(update.effective_user.id)
        if user_id != str(OWNER_TELEGRAM_ID):
            await update.message.reply_text(
                "❌ مو أنت المالك! ما تقدر توقف الشبح."
            )
            return

        self.ghost_active = False
        await update.message.reply_text(
            "👻 Ghost موقّف! 🔴\n"
            "لما بدك تشغلني، ارسل /شغل"
        )
        logger.info("🔴 Ghost تم إيقافه")

    # ========================================================
    # أوامر تيليجرام
    # ========================================================

    async def cmd_start(self, update, context):
        """رسالة البداية"""
        user = update.effective_user
        user_id = str(user.id)

        if user_id == str(OWNER_TELEGRAM_ID):
            text = (
                f"أهلاً يا {OWNER_NAME}! 👻\n\n"
                f"أنا {GHOST_NAME}، مساعدك الشخصي.\n\n"
                f"🔍 أوامرك:\n"
                f"/شغل — تشغيل الشبح ✅\n"
                f"/وقف — إيقاف الشبح 🔴\n"
                f"/مهام — عرض المهام\n"
                f"/مواعيد — عرض المواعيد\n"
                f"/اشتراكات — عرض الاشتراكات\n"
                f"/حالة — حالة الشبح\n"
                f"/مساعدة — قائمة الأوامر"
            )
        else:
            text = (
                f"أهلاً! أنا {GHOST_NAME}، المساعد الشخصي "
                f"لـ {OWNER_NAME} 👻\n\n"
                f"كيف فيني أساعدك؟"
            )

        await update.message.reply_text(text)

    async def cmd_help(self, update, context):
        """قائمة المساعدة"""
        user_id = str(update.effective_user.id)

        if user_id == str(OWNER_TELEGRAM_ID):
            text = (
                "🔍 أوامر الشبح:\n\n"
                "/شغل — تشغيل الشبح ✅\n"
                "/وقف — إيقاف الشبح 🔴\n"
                "/حالة — حالة الشبح\n"
                "/مهام — عرض المهام\n"
                "/مواعيد — عرض المواعيد\n"
                "/اشتراكات — عرض الاشتراكات\n"
                "/نظام — تذكير NSsFOREX\n\n"
                "أو ارسل أي رسالة وكلامك!"
            )
        else:
            text = (
                "كيف فيني أساعدك؟\n\n"
                "ارسل رسالتك وبردا عليك! 👻"
            )

        await update.message.reply_text(text)

    async def cmd_status(self, update, context):
        """حالة Ghost"""
        user_id = str(update.effective_user.id)
        if user_id != str(OWNER_TELEGRAM_ID):
            await update.message.reply_text("👻 Ghost شغال!")
            return

        if self.ghost_active:
            status = "✅ شغال"
        else:
            status = "🔴 موقّف"

        text = (
            f"👻 حالة الشبح:\n\n"
            f"الوضع: {status}\n"
        )

        if self.tasks and hasattr(self.tasks, "get_status"):
            text += f"المهام: {self.tasks.get_status()}\n"
        if self.appointments and hasattr(self.appointments, "get_status"):
            text += f"المواعيد: {self.appointments.get_status()}\n"
        if self.subscriptions and hasattr(self.subscriptions, "get_status"):
            text += f"الاشتراكات: {self.subscriptions.get_status()}\n"

        await update.message.reply_text(text)

    async def cmd_tasks(self, update, context):
        """عرض المهام"""
        if not self.tasks:
            await update.message.reply_text("❌ نظام المهام مو جاهز")
            return

        tasks = self.tasks.list_tasks()
        if not tasks:
            await update.message.reply_text("📝 ما عندك مهام حالياً")
            return

        text = "📝 مهامك:\n\n"
        for i, task in enumerate(tasks, 1):
            status = "✅" if task.get("done") else "⬜"
            text += f"{i}. {status} {task.get('title', task)}\n"

        await update.message.reply_text(text)

    async def cmd_appointments(self, update, context):
        """عرض المواعيد"""
        if not self.appointments:
            await update.message.reply_text("❌ نظام المواعيد مو جاهز")
            return

        appointments = self.appointments.list_appointments()
        if not appointments:
            await update.message.reply_text("📅 ما عندك مواعيد حالياً")
            return

        text = "📅 مواعيدك:\n\n"
        for i, appt in enumerate(appointments, 1):
            text += (
                f"{i}. {appt.get('title', appt)} — "
                f"{appt.get('date', '')}\n"
            )

        await update.message.reply_text(text)

    async def cmd_subscriptions(self, update, context):
        """عرض الاشتراكات"""
        if not self.subscriptions:
            await update.message.reply_text(
                "❌ نظام الاشتراكات مو جاهز"
            )
            return

        subs = self.subscriptions.list_subscriptions()
        if not subs:
            await update.message.reply_text("💳 ما عندك اشتراكات")
            return

        text = "💳 اشتراكاتك:\n\n"
        for i, sub in enumerate(subs, 1):
            status = "🟢" if sub.get("active") else "🔴"
            text += (
                f"{i}. {status} {sub.get('name', sub)} — "
                f"{sub.get('price', '')}\n"
            )

        await update.message.reply_text(text)

    async def cmd_nss(self, update, context):
        """تذكير NSsFOREX"""
        text = (
            "📈 NSsFOREX — تذكير!\n\n"
            f"تيليجرام: {NS_LINKS['telegram']}\n"
            f"Linktree: {NS_LINKS['linktree']}\n"
            f"نيسال: {NS_LINKS['owner']}\n\n"
            f"🔔 تذكير الاشتراك: قبل {SUB_REMINDER_DAYS} يوم"
        )
        await update.message.reply_text(text)

    # ========================================================
    # الرسائل العادية
    # ========================================================

    async def handle_message(self, update, context):
        """معالجة الرسائل"""
        # --- فحص إذا Ghost موقّف ---
        if not self.ghost_active:
            user_id = str(update.effective_user.id)
            if user_id == str(OWNER_TELEGRAM_ID):
                await update.message.reply_text(
                    "🔴 أنا موقّف حالياً.\n"
                    "شغلني بـ /شغل"
                )
            else:
                await update.message.reply_text(
                    self.off_message
                )
            return

        # --- معالجة عادية ---
        message_text = update.message.text
        user = update.effective_user
        sender_name = user.first_name
        user_id = str(user.id)
        is_owner = user_id == str(OWNER_TELEGRAM_ID)

        # حفظ بالذاكرة
        if self.memory:
            self.memory.save_message(
                sender=sender_name,
                message=message_text,
                platform="telegram",
                is_owner=is_owner
            )

        # توليد الرد
        if self.brain:
            response = self.brain.think(
                message=message_text,
                sender_name=sender_name,
                platform="telegram",
                is_owner=is_owner,
                lang="ar"
            )
        else:
            response = "👻 ما في عقل! شوف العقل."

        # حفظ الرد
        if self.memory:
            self.memory.save_message(
                sender=GHOST_NAME,
                message=response,
                platform="telegram",
                is_ghost=True
            )

        await update.message.reply_text(response)

    # ========================================================
    # استقبال رسالة من واتساب (جسر واتساب→تيليجرام)
    # ========================================================

    async def send_to_owner(self, text):
        """إرسال رسالة للمالك على تيليجرام"""
        if self.app and OWNER_TELEGRAM_ID:
            try:
                await self.app.bot.send_message(
                    chat_id=OWNER_TELEGRAM_ID,
                    text=text
                )
                logger.info("📩 رسالة مرسلة للمالك على تيليجرام")
                return True
            except Exception as e:
                logger.error(f"❌ خطأ إرسال تيليجرام: {e}")
        return False

    async def forward_whatsapp_to_telegram(
        self, sender_phone, message
    ):
        """تحويل رسالة واتساب لتيليجرام"""
        text = (
            f"💬 رسالة واتساب جديدة!\n\n"
            f"📞 من: {sender_phone}\n"
            f"📝 الرسالة: {message}\n\n"
            f"---\n"
        )

        # يلقي الجواب من العقل
        if self.brain and self.ghost_active:
            response = self.brain.think(
                message=message,
                sender_name=sender_phone,
                platform="whatsapp",
                lang="ar"
            )
            text += f"👻 رد Ghost:\n{response}"
        else:
            text += "🔴 Ghost موقّف حالياً"

        await self.send_to_owner(text)

    # ========================================================
    # تشغيل البوت
    # ========================================================

    def setup(self):
        """إعداد البوت"""
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN ناقص")
            return False

        self.app = (
            Application.builder()
            .token(self.token)
            .build()
        )

        # أوامر المالك
        self.app.add_handler(
            CommandHandler("شغل", self.cmd_ghost_on)
        )
        self.app.add_handler(
            CommandHandler("وقف", self.cmd_ghost_off)
        )

        # أوامر عامة
        self.app.add_handler(
            CommandHandler("start", self.cmd_start)
        )
        self.app.add_handler(
            CommandHandler("help", self.cmd_help)
        )
        self.app.add_handler(
            CommandHandler("مساعدة", self.cmd_help)
        )
        self.app.add_handler(
            CommandHandler("حالة", self.cmd_status)
        )
        self.app.add_handler(
            CommandHandler("مهام", self.cmd_tasks)
        )
        self.app.add_handler(
            CommandHandler("مواعيد", self.cmd_appointments)
        )
        self.app.add_handler(
            CommandHandler("اشتراكات", self.cmd_subscriptions)
        )
        self.app.add_handler(
            CommandHandler("نظام", self.cmd_nss)
        )

        # رسائل عادية
        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message
            )
        )

        logger.info("✅ أوامر تيليجرام جاهزة")
        return True

    async def start(self):
        """تشغيل البوت"""
        if self.setup():
            logger.info("📱 Ghost Telegram يشتغل...")
            await self.app.run_polling()

    def get_status(self):
        """حالة تيليجرام"""
        if not self.token:
            return "❌ TELEGRAM_BOT_TOKEN ناقص"

        if self.ghost_active:
            return "✅ تيليجرام شغال"
        else:
            return "🔴 تيليجرام موقّف (الشبح نايم)"
