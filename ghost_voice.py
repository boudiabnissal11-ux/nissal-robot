# ============================================================
# Ghost Voice — صوت الشبح
# تحويل النص لصوت باستخدام Edge TTS
# ============================================================

import os
import re
import time

from config import DEFAULT_LANGUAGE, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID


class GhostVoice:
    """صوت Ghost — تحويل الرد النصي إلى صوت"""

    # الأصوات المستخدمة في Edge TTS
    # العربية: صوت لبناني رجولي
    EDGE_VOICE_MAP = {
        "ar": "ar-LB-RamiNeural",
        "lb": "ar-LB-RamiNeural",
        "en": "en-US-GuyNeural",
        "fr": "fr-FR-HenriNeural",
    }

    def __init__(self):
        self.default_lang = DEFAULT_LANGUAGE
        self.elevenlabs_key = ELEVENLABS_API_KEY
        self.elevenlabs_voice = ELEVENLABS_VOICE_ID

        self.voice_dir = "data/voice"
        os.makedirs(self.voice_dir, exist_ok=True)

    def _clean_text(self, text):
        """تنظيف النص من الإيموجي قبل إرساله للـ TTS"""
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001FAFF"
            "\U00002600-\U000027BF"
            "\U0001F1E6-\U0001F1FF"
            "]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub("", text)
        text = re.sub(r"[*_#`]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    async def speak(self, text, lang=None):
        """تحويل النص لصوت — Edge TTS أولاً، ثم ElevenLabs"""

        if lang is None:
            lang = self.default_lang

        # توحيد اللغة العربية
        if lang in ("arabic", "Arabic"):
            lang = "ar"

        if lang in ("lebanese", "Lebanese"):
            lang = "lb"

        text = self._clean_text(text)

        # ----------------------------------------------------
        # Edge TTS — الخيار الأساسي
        # ----------------------------------------------------
        try:
            return await self._edge_tts_speak(text, lang)

        except Exception as e:
            print(f"⚠️ Edge TTS failed: {e}")

        # ----------------------------------------------------
        # ElevenLabs — احتياط
        # ----------------------------------------------------
        if self.elevenlabs_key and self.elevenlabs_voice:
            try:
                return await self._elevenlabs_tts(text, lang)

            except Exception as e:
                print(f"⚠️ ElevenLabs failed: {e}")

        return "⚠️ ما قدرت أحوّل الرد لصوت"

    async def _edge_tts_speak(self, text, lang):
        """تحويل النص لصوت باستخدام Edge TTS"""

        import edge_tts

        # إذا اللغة غير موجودة، استخدم العربي اللبناني
        voice = self.EDGE_VOICE_MAP.get(
            lang,
            self.EDGE_VOICE_MAP["ar"]
        )

        filename = os.path.join(
            self.voice_dir,
            f"voice_{int(time.time() * 1000)}.mp3"
        )

        print(f"🔊 Edge TTS: {voice}")

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="+25%",
        )

        await communicate.save(filename)

        if not os.path.exists(filename):
            raise Exception("Edge TTS لم ينشئ ملف الصوت")

        if os.path.getsize(filename) == 0:
            raise Exception("ملف الصوت فارغ")

        return filename

    async def _elevenlabs_tts(self, text, lang):
        """تحويل النص لصوت باستخدام ElevenLabs API"""

        import httpx

        url = (
            f"https://api.elevenlabs.io/v1/text-to-speech/"
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
                "speed": 1.15,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        if response.status_code == 200:

            filename = os.path.join(
                self.voice_dir,
                f"voice_el_{int(time.time() * 1000)}.mp3"
            )

            with open(filename, "wb") as f:
                f.write(response.content)

            return filename

        raise Exception(
            f"ElevenLabs error: {response.status_code}"
        )

    def get_status(self):
        """حالة الصوت"""

        has_eleven = "✅" if self.elevenlabs_key else "❌"

        return f"{has_eleven} ElevenLabs | Edge TTS: متاح"
