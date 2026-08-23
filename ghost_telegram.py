# ============================================================
# Ghost Telegram — تلغرام الشبح
# بوت تلغرام — الاتصال الرئيسي
# ============================================================

import os
import asyncio
import logging
from datetime import datetime
from config import (
    OWNER_NAME, GHOST_NAME, OWNER_TELEGRAM_ID, NS_LINKS
)

logger = logging.getLogger(__name__)

try:
    from telegram import Update, Bot
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        ContextTypes, filters
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("⚠️ python-telegram-bot مو مثبت")


class GhostTelegram:
    """تلغرام Ghost — بوت تلغرام"""

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

        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.owner_id = int(OWNER_TELEGRAM_ID)
        self.app = None
        self.bot = None

    def _is_owner(self, user_id):
        """هل المستخدم هو المالك؟"""
        return user_id == self.owner_id

    async def start(self, update: Update,
                    context: ContextTypes.DEFAULT_TYPE):
        """أمر /start"""
        user = update.effective_user
        user_id = user.id

        if self._is_owner(user_id):
            await update.message.reply_text(
                f"👻 أهلا {OWNER_NAME}! أنا Ghost — شبحك الشخصي!\n\n"
                f"بقدر أساعدك بـ:\n"
                f"📋 المهام\n📅 المواعيد\n👥 الاشتراكات\n"
                f"💳 الدفعات\n🧠 الذواكر\n\n"
                f"أو بس حكيلي شو بدك! 👻"
            )
        else:
            await update.message.reply_text(
                f"👻 أهلا! أنا Ghost — بوت NSsFOREX!\n\n"
                f"للاشتراك والتفاصيل:\n"
                f"📱 {NS_LINKS['telegram']}\n"
                f"🌐 {NS_LINKS['linktree']}\n"
                f"💬 {NS_LINKS['owner']}"
            )

    async def help_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        """أمر /help"""
        user_id = update.effective_user.id

        if self._is_owner(user_id):
            help_text = (
                "👻 أوامر Ghost:\n\n"
                "📋 /tasks — المهام\n"
                "📋 /add_task [عنوان] — مهمة جديدة\n"
                "📋 /done_task [رقم] — إكمال مهمة\n\n"
                "📅 /appointments — المواعيد\n"
                "📅 /add_appointment [عنوان] [تاريخ] — موعد جديد\n\n"
                "👥 /subs — الاشتراكات\n"
                "👥 /add_sub [اسم] [خطة] — اشتراك جديد\n\n"
                "💳 /payments — الدفعات\n"
                "💳 /add_payment [عنوان] [مبلغ] — دفعة جديدة\n\n"
                "🧠 /memory — الذواكر\n"
                "🧠 /status — حالة الشبح\n"
                "🧠 /clear — مسح المحادثة\n\n"
                "أو بس حكيلي وأنا بفهمك! 👻"
            )
        else:
            help_text = (
                "👻 أوامر:\n\n"
                "/start — البداية\n"
                "/help — المساعدة\n"
                "/subscribe — الاشتراك\n\n"
                "للاستفسار:\n"
                f"💬 {NS_LINKS['owner']}"
            )

        await update.message.reply_text(help_text)

    async def tasks_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """أمر /tasks"""
        if not self._is_owner(update.effective_user.id):
            return

        if self.tasks:
            text = self.tasks.format_tasks_list(lang="lb")
        else:
            text = "📋 المهام مو جاهزة بعد"

        await update.message.reply_text(text)

    async def add_task_command(self, update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
        """أمر /add_task"""
        if not self._is_owner(update.effective_user.id):
            return

        title = " ".join(context.args) if context.args else ""
        if not title:
            await update.message.reply_text(
                "📋 اكتب: /add_task [عنوان المهمة]"
            )
            return

        if self.tasks:
            task = self.tasks.add_task(title)
            await update.message.reply_text(
                f"✅ مهمة جديدة: {task['title']} 👻"
            )
        else:
            await update.message.reply_text("📋 المهام مو جاهزة بعد")

    async def done_task_command(self, update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
        """أمر /done_task"""
        if not self._is_owner(update.effective_user.id):
            return

        if not self.tasks:
            return

        pending = self.tasks.get_pending_tasks()
        if not context.args:
            await update.message.reply_text(
                "📋 اكتب: /done_task [رقم]\n\n"
                + self.tasks.format_tasks_list(pending, lang="lb")
            )
            return

        try:
            idx = int(context.args[0]) - 1
            if 0 <= idx < len(pending):
                task = self.tasks.complete_task(pending[idx]["id"])
                await update.message.reply_text(
                    f"✅ مكتملة: {task['title']} 👻"
                )
        except (ValueError, IndexError):
            await update.message.reply_text("⚠️ رقم غلط")

    async def appointments_command(self, update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
        """أمر /appointments"""
        if not self._is_owner(update.effective_user.id):
            return

        if self.appointments:
            text = self.appointments.format_appointments_list(
                lang="lb"
            )
        else:
            text = "📅 المواعيد مو جاهزة بعد"

        await update.message.reply_text(text)

    async def subs_command(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        """أمر /subs"""
        if not self._is_owner(update.effective_user.id):
            return

        if self.subscriptions:
            text = self.subscriptions.format_subscriptions_list(
                lang="lb"
            )
        else:
            text = "👥 الاشتراكات مو جاهزة بعد"

        await update.message.reply_text(text)

    async def payments_command(self, update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
        """أمر /payments"""
        if not self._is_owner(update.effective_user.id):
            return

        if self.pay:
            text = self.pay.format_payments_list(lang="lb")
        else:
            text = "💳 الدفعات مو جاهزة بعد"

        await update.message.reply_text(text)

    async def memory_command(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        """أمر /memory"""
        if not self._is_owner(update.effective_user.id):
            return

        if self.memory:
            count = self.memory.get_memory_count()
            await update.message.reply_text(
                f"🧠 {count} ذاكرة محفوظة 👻"
            )
        else:
            await update.message.reply_text("🧠 الذاكرة مو جاهزة بعد")

    async def status_command(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        """أمر /status"""
        if not self._is_owner(update.effective_user.id):
            return

        lines = [f"👻 حالة Ghost:\n"]

        if self.brain:
            lines.append(self.brain.get_brain_status())
        if self.tasks:
            lines.append(self.tasks.get_tasks_summary(lang="lb"))
        if self.appointments:
            lines.append(
                self.appointments.get_appointments_summary(lang="lb")
            )
        if self.subscriptions:
            lines.append(
                self.subscriptions.get_subscriptions_summary(lang="lb")
            )
        if self.pay:
            lines.append(self.pay.get_pay_summary(lang="lb"))

        await update.message.reply_text("\n".join(lines))

    async def clear_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """أمر /clear"""
        if not self._is_owner(update.effective_user.id):
            return

        if self.brain:
            self.brain.clear_history()
            await update.message.reply_text("🧹 المحادثة ممسوحة! 👻")

    async def subscribe_command(self, update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
        """أمر /subscribe — للعملاء"""
        await update.message.reply_text(
            "👻 اشتراك NSsFOREX:\n\n"
            f"📱 تلغرام: {NS_LINKS['telegram']}\n"
            f"🌐 كل الروابط: {NS_LINKS['linktree']}\n"
            f"💬 تواصل: {NS_LINKS['owner']}\n\n"
            "نورتنا! 🔥"
        )

    async def handle_message(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        """الرد على الرسائل العادية"""
        user = update.effective_user
        message = update.message.text

        if not message:
            return

        sender_name = user.first_name or user.username or "مستخدم"
        user_id = user.id

        if self.brain:
            is_owner = self._is_owner(user_id)
            response = self.brain.think(
                message=message,
                sender_name=sender_name if is_owner else None,
                platform="telegram",
                lang=None
            )
        else:
            if self._is_owner(user_id):
                response = "👻 الدماغ مو جاهز بعد..."
            else:
                response = (
                    f"👻 شكراً لرسالتك! للاشتراك:\n"
                    f"📱 {NS_LINKS['telegram']}\n"
                    f"🌐 {NS_LINKS['linktree']}"
                )

        await update.message.reply_text(response)

    async def send_reminder(self, chat_id, message):
        """إرسال تذكير"""
        try:
            if self.bot:
                await self.bot.send_message(
                    chat_id=chat_id, text=message
                )
                logger.info(f"🔔 تذكير مرسل لـ {chat_id}")
        except Exception as e:
            logger.error(f"❌ خطأ بإرسال التذكير: {e}")

    async def check_and_remind(self):
        """فحص وإرسال التذكيرات"""
        if not self.bot:
            return

        reminders_sent = []

        # تذكيرات المهام
        if self.tasks:
            task_reminders = self.tasks.get_reminders()
            for task in task_reminders:
                msg = f"⏰ تذكير: {task['title']}"
                await self.send_reminder(self.owner_id, msg)
                reminders_sent.append(("task", task["id"]))

        # تذكيرات المواعيد
        if self.appointments:
            apt_reminders = self.appointments.get_reminders()
            for apt in apt_reminders:
                msg = f"📅 موعد قريب: {apt['title']}"
                await self.send_reminder(self.owner_id, msg)
                reminders_sent.append(("appointment", apt["id"]))

        # تذكيرات الاشتراكات
        if self.subscriptions:
            sub_reminders = self.subscriptions.get_reminders(
                lang="lb"
            )
            for reminder in sub_reminders:
                client_id = reminder.get("client_id")
                platform = reminder.get("platform", "telegram")
                if platform == "telegram" and client_id:
                    try:
                        await self.send_reminder(
                            int(client_id), reminder["message"]
                        )
                    except (ValueError, TypeError):
                        pass
                # إرسال نسخة للمالك كمان
                await self.send_reminder(
                    self.owner_id,
                    f"📋 تذكير اشتراك: {reminder['subscription']['client_name']}"
                )
                reminders_sent.append(
                    ("subscription", reminder["subscription"]["id"])
                )

        return reminders_sent

    def setup(self):
        """إعداد البوت"""
        if not TELEGRAM_AVAILABLE:
            logger.error("❌ python-telegram-bot مو مثبت")
            return False

        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN فارغ")
            return False

        self.app = Application.builder().token(self.token).build()
        self.bot = self.app.bot

        # أوامر المالك
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(
            CommandHandler("tasks", self.tasks_command)
        )
        self.app.add_handler(
            CommandHandler("add_task", self.add_task_command)
        )
        self.app.add_handler(
            CommandHandler("done_task", self.done_task_command)
        )
        self.app.add_handler(
            CommandHandler("appointments", self.appointments_command)
        )
        self.app.add_handler(
            CommandHandler("subs", self.subs_command)
        )
        self.app.add_handler(
            CommandHandler("payments", self.payments_command)
        )
        self.app.add_handler(
            CommandHandler("memory", self.memory_command)
        )
        self.app.add_handler(
            CommandHandler("status", self.status_command)
        )
        self.app.add_handler(
            CommandHandler("clear", self.clear_command)
        )
        self.app.add_handler(
            CommandHandler("subscribe", self.subscribe_command)
        )

        # الرسائل العادية
        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message
            )
        )

        logger.info("✅ بوت تلغرام جاهز")
        return True

    def run(self):
        """تشغيل البوت"""
        if self.setup():
            logger.info("👻 Ghost Telegram شغال...")
            self.app.run_polling()
        else:
            logger.error("❌ ما نقدر نشغّل البوت")
