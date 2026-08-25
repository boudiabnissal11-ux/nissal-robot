# ============================================================
# Ghost Telegram — تيليجرام الشبح
# البوت اللي بيتواصل مع الناس
# يدعم: نص + فويس نوت (يرد بصوت)
# ============================================================
import os
import logging
import tempfile
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

    # ========================================================
    # معالجة الرسائل النصية
    # ========================================================
    async def handle_message(self, update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية الواردة"""
        user = update.effective_user
        message = update.effective_message
        text = message.text if message and message.text else ""

        if not text:
            return

        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)
        lang = self.personality.detect_language(text) if self.personality else "lb"

        sender_name = user.first_name or ""
        if self.memory:
            self.memory.save_message(
                sender=sender_name,
                message=text,
                platform="telegram",
                is_owner=is_owner
            )

        if is_owner:
            if self.personality:
                self.personality.learn_style(text, source="owner")
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
            if self.brain:
                reply = await self.brain.think(
                    user_message=text,
                    lang=lang,
                    sender_name=sender_name,
                    platform="telegram"
                )
            else:
                reply = "⚠️ Ghost مو شغال حالياً"

        if message:
            await message.reply_text(reply)

        if self.memory:
            self.memory.save_message(
                sender="Ghost",
                message=reply,
                platform="telegram",
                is_ghost=True
            )

    # ========================================================
    # معالجة الفويس نوت — يسمع ويرد بصوت!
    # ========================================================
    async def handle_voice(self, update: Update,
                           context: ContextTypes.DEFAULT_TYPE):
        """معالجة رسائل الصوت (فويس نوت)"""
        user = update.effective_user
        message = update.effective_message
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        # 1. حمّل الملف الصوتي
        voice = message.voice or message.audio
        if not voice:
            await message.reply_text("⚠️ ما قدرت أسمع الصوت!")
            return

        # بتشخّص إنو الشبح عم يفكّر
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # 2. نزل الملف
        try:
            voice_file = await voice.get_file()
            tmp_dir = tempfile.mkdtemp()
            ogg_path = os.path.join(tmp_dir, "voice.ogg")
            await voice_file.download_to_drive(ogg_path)
        except Exception as e:
            logger.error(f"خطأ بتحميل الصوت: {e}")
            await message.reply_text("⚠️ ما قدرت أحمل الصوت!")
            return

        # 3. حوّل OGG لـ WAV (faster-whisper بيحتاج WAV)
        try:
            from pydub import AudioSegment
            wav_path = os.path.join(tmp_dir, "voice.wav")
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(wav_path, format="wav")
        except Exception as e:
            logger.error(f"خطأ بتحويل الصوت: {e}")
            await message.reply_text("⚠️ ما قدرت أقرأ الصوت!")
            return

        # 4. حوّل الصوت لنص (Speech-to-Text)
        try:
            from faster_whisper import WhisperModel

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

segments, info = model.transcribe(
    wav_path,
    language="ar",
    beam_size=5,
    vad_filter=True
)

transcribed_text = " ".join(
    seg.text.strip() for seg in segments
).strip()
            logger.info(f"📝 النص من الصوت: {transcribed_text}")
        except Exception as e:
            logger.error(f"خطأ بتحويل الصوت لنص: {e}")
            await message.reply_text("⚠️ ما قدرت أفهم الصوت!")
            return

        if not transcribed_text:
            await message.reply_text("⚠️ ما سمعت شي بالصوت!")
            return

        # 5. فكّر بالرد
        lang = self.personality.detect_language(transcribed_text) if self.personality else "lb"
        sender_name = user.first_name or ""

        if self.memory:
            self.memory.save_message(
                sender=sender_name,
                message=f"[صوت] {transcribed_text}",
                platform="telegram",
                is_owner=is_owner
            )

        if is_owner:
            if self.brain:
                reply = await self.brain.think(
                    user_message=transcribed_text,
                    lang=lang,
                    sender_name=OWNER_NAME,
                    platform="telegram"
                )
            else:
                reply = "⚠️ العقل مو شغال!"
        else:
            if self.brain:
                reply = await self.brain.think(
                    user_message=transcribed_text,
                    lang=lang,
                    sender_name=sender_name,
                    platform="telegram"
                )
            else:
                reply = "⚠️ Ghost مو شغال حالياً"

        # 6. حوّل الرد لصوت (Text-to-Speech)
        try:
            voice_path = await self.voice.speak(reply, lang=lang)
            if voice_path and os.path.exists(voice_path):
                # أرسل كفويس نوت
                with open(voice_path, "rb") as vf:
                    await message.reply_voice(vf)
                # كمان أرسل النص عشان يكون واضح
                await message.reply_text(f"👻 {reply}")
            else:
                # لو الصوت ما اشتغل — أرسل نص فقط
                await message.reply_text(reply)
        except Exception as e:
            logger.error(f"خطأ بصوت الرد: {e}")
            # أرسل نص حتى لو الصوت فشل
            await message.reply_text(reply)

        # 7. احفظ رد Ghost
        if self.memory:
            self.memory.save_message(
                sender="Ghost",
                message=reply,
                platform="telegram",
                is_ghost=True
            )

        # 8. نظّف الملفات المؤقتة
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

    # ========================================================
    # أوامر البوت
    # ========================================================
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

    async def handle_activate(self, update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
        """أمر /on — تفعيل Ghost"""
        user = update.effective_user
        is_owner = str(user.id) == str(OWNER_TELEGRAM_ID)

        if not is_owner:
            await update.message.reply_text("⛔ هاد الأمر للمالك فقط!")
            return

        context.bot_data["ghost_active"] = True
        greeting = self.personality.get_greeting("lb") if self.personality else "شبح مفعّل!"
        await update.message.reply_text(
            f"{greeting}\n\n"
            f"✅ Ghost شغال يا {OWNER_NAME}! 👻\n"
            f"🎤 ابعتلي فويس نوت وبيردلك بصوت!"
        )

    async def handle_deactivate(self, update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
        """أمر /off — إيقاف Ghost"""
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

    async def forward_to_owner(self, message):
        """تحويل رسالة لنصال على تيليجرام"""
        logger.info(f"تحويل لنصال على تيليجرام: {message[:50]}")
        return True

    def get_status(self):
        """حالة تيليجرام"""
        return "✅ تيليجرام جاهز — نص + فويس نوت"
