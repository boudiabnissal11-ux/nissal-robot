# ============================================================
# Ghost Voice — صوت الشبح
# تحويل النص لصوت ومحادثة صوتية
# ============================================================

import os
import asyncio
import logging
from datetime import datetime
from config import OWNER_NAME, DEFAULT_LANGUAGE, GHOST_NAME

logger = logging.getLogger(__name__)


class GhostVoice:
    """صوت Ghost — تحويل النص لصوت"""

    def __init__(self):
        self.enabled = os.environ.get("VOICE_ENABLED", "true").lower() == "true"
        self.engine = os.environ.get("VOICE_ENGINE", "gtts")
        self.language = DEFAULT_LANGUAGE
        self.voice_dir = os.environ.get("VOICE_DIR", "voice_cache")
        os.makedirs(self.voice_dir, exist_ok=True)

    def text_to_speech(self, text, lang=None, voice_style="default"):
        """تحويل النص لصوت"""
        if not self.enabled:
            logger.info("🔇 الصوت معطّل")
            return None

        if lang is None:
            lang = self.language

        try:
            if self.engine == "gtts":
                return self._gtts_speak(text, lang)
            elif self.engine == "elevenlabs":
                return self._elevenlabs_speak(text, lang, voice_style)
            else:
                return self._gtts_speak(text, lang)
        except Exception as e:
            logger.error(f"❌ خطأ بالصوت: {e}")
            return None

    def _gtts_speak(self, text, lang):
        """صوت عبر gTTS"""
        try:
            from gtts import gTTS

            lang_map = {
                "lb": "ar", "ar": "ar",
                "en": "en", "fr": "fr",
                "es": "es"
            }
            gtts_lang = lang_map.get(lang, "ar")

            filename = f"voice_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            filepath = os.path.join(self.voice_dir, filename)

            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(filepath)

            logger.info(f"🔊 صوت محفوظ: {filename}")
            return filepath

        except ImportError:
            logger.warning("⚠️ gTTS مو مثبت — جرّب: pip install gTTS")
            return None
        except Exception as e:
            logger.error(f"❌ gTTS Error: {e}")
            return None

    def _elevenlabs_speak(self, text, lang, voice_style="default"):
        """صوت عبر ElevenLabs"""
        api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "")

        if not api_key or not voice_id:
            logger.warning("⚠️ ElevenLabs مفاتيح ناقصة")
            return self._gtts_speak(text, lang)

        try:
            import httpx

            filename = f"voice_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            filepath = os.path.join(self.voice_dir, filename)

            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }

            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload
                )
                resp.raise_for_status()

                with open(filepath, "wb") as f:
                    f.write(resp.content)

            logger.info(f"🔊 ElevenLabs صوت محفوظ: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"❌ ElevenLabs Error: {e}")
            return self._gtts_speak(text, lang)

    def speech_to_text(self, audio_path, lang=None):
        """تحويل الصوت لنص"""
        if lang is None:
            lang = self.language

        try:
            import whisper

            whisper_lang_map = {
                "lb": "ar", "ar": "ar",
                "en": "en", "fr": "fr"
            }
            whisper_lang = whisper_lang_map.get(lang, None)

            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language=whisper_lang)
            text = result["text"].strip()

            logger.info(f"🎤 نص مستخرج: {text[:50]}...")
            return text

        except ImportError:
            logger.warning("⚠️ Whisper مو مثبت — جرّب: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"❌ Whisper Error: {e}")
            return None

    def get_voice_status(self):
        """حالة الصوت"""
        if not self.enabled:
            return "🔇 الصوت معطّل"

        status_parts = []
        status_parts.append(f"🔊 محرك: {self.engine}")

        if self.engine == "gtts":
            status_parts.append("✅ gTTS جاهز")
        elif self.engine == "elevenlabs":
            has_key = bool(os.environ.get("ELEVENLABS_API_KEY"))
            has_voice = bool(os.environ.get("ELEVENLABS_VOICE_ID"))
            if has_key and has_voice:
                status_parts.append("✅ ElevenLabs جاهز")
            else:
                status_parts.append("⚠️ ElevenLabs ناقص مفاتيح")

        return " | ".join(status_parts)

    async def text_to_speech_async(self, text, lang=None):
        """تحويل نص لصوت — غير متزامن"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.text_to_speech, text, lang
        )
