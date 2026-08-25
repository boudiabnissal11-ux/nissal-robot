# ============================================================
# Ghost Voice — صوت الشبح
# ElevenLabs أولاً — بدون gTTS أثناء الاختبار
# ============================================================

import os
import time

from config import (
    DEFAULT_LANGUAGE,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)


class GhostVoice:
    """صوت Ghost — ElevenLabs"""

    def __init__(self):
        self.default_lang = DEFAULT_LANGUAGE
        self.elevenlabs_key = ELEVENLABS_API_KEY
        self.elevenlabs_voice = ELEVENLABS_VOICE_ID

        self.voice_dir = "data/voice"
        os.makedirs(self.voice_dir, exist_ok=True)

    async def speak(self, text, lang=None):
        """تحويل النص لصوت باستخدام ElevenLabs"""

        if lang is None:
            lang = self.default_lang

        print(f"🔊 Ghost Voice: lang={lang}")
        print(f"🎙️ ElevenLabs Voice ID: {'SET' if self.elevenlabs_voice else 'EMPTY'}")
        print(f"📝 النص: {text}")

        if not self.elevenlabs_key:
            raise Exception("ELEVENLABS_API_KEY غير موجود")

        if not self.elevenlabs_voice:
            raise Exception("ELEVENLABS_VOICE_ID غير موجود")

        try:
            filename = await self._elevenlabs_tts(text, lang)

            print(f"✅ ElevenLabs نجح: {filename}")

            return filename

        except Exception as e:
            print(f"❌ ElevenLabs فشل: {e}")
            raise

    async def _elevenlabs_tts(self, text, lang):
        """تحويل النص لصوت باستخدام ElevenLabs API"""

        import httpx

        url = (
            "https://api.elevenlabs.io/v1/text-to-speech/"
            f"{self.elevenlabs_voice}"
        )

        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8,
            },
        }

        print("🌐 جاري الاتصال بـ ElevenLabs...")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            try:
                error_text = response.text
            except Exception:
                error_text = "Unknown error"

            raise Exception(
                f"HTTP {response.status_code}: {error_text}"
            )

        if not response.content:
            raise Exception("ElevenLabs أعاد ملفًا فارغًا")

        filename = os.path.join(
            self.voice_dir,
            f"voice_el_{int(time.time() * 1000)}.mp3"
        )

        with open(filename, "wb") as f:
            f.write(response.content)

        if not os.path.exists(filename):
            raise Exception("لم يتم إنشاء ملف الصوت")

        if os.path.getsize(filename) == 0:
            raise Exception("ملف الصوت فارغ")

        return filename

    def get_status(self):
        """حالة الصوت"""

        has_key = "✅" if self.elevenlabs_key else "❌"
        has_voice = "✅" if self.elevenlabs_voice else "❌"

        return (
            f"ElevenLabs API: {has_key} | "
            f"Voice ID: {has_voice}"
        )
