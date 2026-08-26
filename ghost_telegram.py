# ============================================================
# Ghost Telegram — تيليجرام الشبح
# البوت اللي بيتواصل مع الناس
# يدعم: نص + فويس نوت (يسمع ويرد بصوت)
# ============================================================

import os
import logging
import tempfile
import shutil

from telegram import Update
from telegram.ext import ContextTypes

from config import OWNER_TELEGRAM_ID, OWNER_NAME


logger = logging.getLogger(__name__)


class GhostTelegram:
    """تيليجرام Ghost — بيتواصل مع الناس"""

    def __init__(
        self,
        core=None,
        memory=None,
        brain=None,
        personality=None,
        voice=None,
        tasks=None,
        appointments=None,
        subscriptions=None,
        pay=None
    ):
        self.core = core
        self.memory = memory
        self.brain = brain
        self.personality = personality
        self.voice = voice
        self.tasks = tasks
        self.appointments = appointments
        self.subscriptions = subscriptions
        self.pay = pay

        # ====================================================
        # Whisper — نحمّل الموديل مرة واحدة فقط
        # ====================================================
        self.whisper_model = None

    # ========================================================
    # تحميل Whisper
    # ========================================================

    def _get_whisper_model(self):
        """تحميل Whisper مرة واحدة وإعادة استخدامه"""

        if self.whisper_model is not None:
            return self.whisper_model

        from faster_whisper import WhisperModel

        logger.info("🎤 تحميل Whisper model...")

        self.whisper_model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

        logger.info("✅ Whisper جاهز")

        return self.whisper_model

    # ========================================================
    # معالجة الرسائل النصية
    # ========================================================

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة الرسائل النصية الواردة — عبر غوست كور"""

        user = update.effective_user
        message = update.effective_message

        text = message.text if message and message.text else ""
        logger.info(f"📩 وصلت رسالة إلى Ghost: {text}")
        if not text:
            return

        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)
        sender_name = OWNER_NAME if is_owner else (user.first_name or "")

        if not self.core:
            await message.reply_text("⚠️ العقل المركزي غير متصل!")
            return

        reply_text, _ = await self.core.handle_incoming(
            platform="telegram",
            platform_user_id=str(user.id),
            sender_name=sender_name,
            text=text,
            response_type="text",
            is_owner=is_owner,
        )

        if message:
            await message.reply_text(reply_text)

    # ========================================================
    # معالجة الفويس نوت
    # ========================================================

    async def handle_voice(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة رسائل الصوت — يسمع ويرد بصوت — عبر غوست كور"""

        user = update.effective_user
        message = update.effective_message

        if not message:
            return

        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)
        sender_name = OWNER_NAME if is_owner else (user.first_name or "")

        # ====================================================
        # 1. تحديد الملف الصوتي
        # ====================================================

        voice = message.voice or message.audio

        if not voice:
            await message.reply_text(
                "⚠️ ما قدرت أسمع الصوت!"
            )
            return

        tmp_dir = tempfile.mkdtemp(prefix="ghost_voice_")

        try:

            # =================================================
            # 2. تحميل الصوت من Telegram
            # =================================================

            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )

            logger.info("🎤 Ghost عم يحمل الصوت...")

            voice_file = await voice.get_file()

            ogg_path = os.path.join(tmp_dir, "voice.ogg")

            await voice_file.download_to_drive(ogg_path)

            logger.info("✅ تم تحميل الصوت")

            # =================================================
            # 3. تحويل الصوت إلى WAV مناسب لـ Whisper
            # =================================================

            try:

                from pydub import AudioSegment

                wav_path = os.path.join(tmp_dir, "voice.wav")

                audio = AudioSegment.from_file(ogg_path)
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)

                audio.export(
                    wav_path,
                    format="wav",
                    parameters=["-ac", "1", "-ar", "16000"]
                )

                logger.info("✅ تم تحويل الصوت إلى WAV 16kHz Mono")

            except Exception as e:
                logger.error(f"خطأ بتحويل الصوت: {e}")
                await message.reply_text("⚠️ ما قدرت أقرأ الصوت!")
                return

            # =================================================
            # 4. Speech-to-Text بواسطة faster-whisper
            # =================================================

            try:

                logger.info("🧠 Ghost عم يحاول يفهم الصوت...")

                model = self._get_whisper_model()

                segments, info = model.transcribe(
                    wav_path,
                    language="ar",
                    beam_size=1,
                    best_of=1,
                    temperature=0,
                    vad_filter=True,
                    vad_parameters={"min_silence_duration_ms": 500},
                    condition_on_previous_text=False
                )

                transcribed_text = " ".join(
                    seg.text.strip() for seg in segments if seg.text
                ).strip()

                logger.info(f"📝 النص من الصوت: {transcribed_text}")

                if info:
                    logger.info(f"🌐 اللغة المكتشفة: {info.language}")

            except Exception as e:
                logger.exception(f"خطأ بتحويل الصوت لنص: {e}")
                await message.reply_text("⚠️ ما قدرت أفهم الصوت!")
                return

            # =================================================
            # 5. التأكد أن Whisper فهم شيئًا
            # =================================================

            if not transcribed_text:
                await message.reply_text("⚠️ ما سمعت شي بالصوت!")
                return

            # =================================================
            # 6. تمرير الطلب كاملاً لغوست كور
            # =================================================

            if not self.core:
                await message.reply_text("⚠️ العقل المركزي غير متصل!")
                return

            reply_text, voice_path = await self.core.handle_incoming(
                platform="telegram",
                platform_user_id=str(user.id),
                sender_name=sender_name,
                text=transcribed_text,
                response_type="voice",
                is_owner=is_owner,
            )

            # =================================================
            # 7. إرسال الرد الصوتي ثم النصي
            # =================================================

            if voice_path and isinstance(voice_path, str) and os.path.exists(voice_path):
                with open(voice_path, "rb") as vf:
                    await message.reply_voice(vf)
                await message.reply_text(f"👻 {reply_text}")
            else:
                await message.reply_text(reply_text)

        finally:

            # =================================================
            # 8. تنظيف الملفات المؤقتة
            # =================================================

            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            except Exception:
                pass

    # ========================================================
    # أمر /start
    # ========================================================

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /start"""

        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if is_owner:
            greeting = (
                self.personality.get_greeting("lb")
                if self.personality else "أهلاً!"
            )
            await update.message.reply_text(
                f"{greeting}\n\n"
                f"أنا Ghost — الشبح 👻\n"
                f"مساعدك الشخصي يا {OWNER_NAME}!\n\n"
                f"🎤 ابعتلي فويس نوت وبيردلك بصوت!\n"
                f"📝 أو ابعتلي رسالة وبيردلك نص\n\n"
                f"شغّلني بأمر: /on\n"
                f"وقّفني بأمر: /off"
            )
        else:
            await update.message.reply_text(
                "أهلاً! 👻 أنا Ghost — مساعد شخصي.\n"
                "كيف فيني ساعدك؟"
            )

    # ========================================================
    # أمر /on
    # ========================================================

    async def handle_activate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /on — تفعيل Ghost"""

        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if not is_owner:
            await update.message.reply_text("⛔ هاد الأمر للمالك فقط!")
            return

        context.bot_data["ghost_active"] = True

        greeting = (
            self.personality.get_greeting("lb")
            if self.personality else "شبح مفعّل!"
        )

        await update.message.reply_text(
            f"{greeting}\n\n"
            f"✅ Ghost شغال يا {OWNER_NAME}! 👻\n"
            f"🎤 ابعتلي فويس نوت وبيردلك بصوت!"
        )

    # ========================================================
    # أمر /off
    # ========================================================

    async def handle_deactivate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر /off — إيقاف Ghost"""

        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if not is_owner:
            await update.message.reply_text("⛔ هاد الأمر للمالك فقط!")
            return

        context.bot_data["ghost_active"] = False

        farewell = (
            self.personality.get_farewell("lb")
            if self.personality else "مع السلامة!"
        )

        await update.message.reply_text(
            f"{farewell}\n\n"
            f"🔴 Ghost وقّف يا {OWNER_NAME}."
        )

    # ========================================================
    # تحويل رسالة للمالك
    # ========================================================

    async def forward_to_owner(self, message):
        """تحويل رسالة لنصال على تيليجرام"""
        logger.info(f"تحويل لنصال على تيليجرام: {message[:50]}")
        return True

    # ========================================================
    # حالة Telegram
    # ========================================================

    def get_status(self):
        """حالة تيليجرام"""
        return "✅ تيليجرام جاهز — نص + فويس نوت (عبر غوست كور)"
