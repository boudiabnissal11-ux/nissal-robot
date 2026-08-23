# ============================================================
# Ghost Voice — صوت الشبح
# تحويل النص لصوت
# ============================================================
import os
from config import DEFAULT_LANGUAGE, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID


class GhostVoice:
    """صوت Ghost — بيتحكي لما نصال بدّه"""

    # خريطة اللغات لـ gTTS
    GTTS_LANG_MAP = {
        "lb": "ar",   # لبناني → عربي (أقرب)
        "ar": "ar",
        "en": "en",
        "fr": "fr",
    }

    def __init__(self):
        self.default_lang = DEFAULT_LANGUAGE
        self.elevenlabs_key = ELEVENLABS_API_KEY
        self.elevenlabs_voice = ELEVENLABS_VOICE_ID
        self.voice_dir = "data/voice"
        os.makedirs(self.voice_dir, exist_ok=True)

    async def speak(self, text, lang=None):
        """تحويل النص لصوت — اولاً ElevenLabs، وبعدين gTTS"""
        if lang is None:
            lang = self.default_lang

        # جرّب ElevenLabs أولاً
        if self.elevenlabs_key and self.elevenlabs_voice:
            try:
                return await self._elevenlabs_tts(text, lang)
            except Exception:
                pass  # لو فشل → gTTS

        # gTTS كـ fallback
        return await self._gtts_speak(text, lang)

    async def _gtts_speak(self, text, lang):
        """تحويل النص لصوت باستخدام gTTS"""
        try:
            from gtts import gTTS
            gtts_lang = self.GTTS_LANG_MAP.get(lang, "ar")
            tts = gTTS(text=text, lang=gtts_lang)
            filename = f"{self.voice_dir}/voice_{int(os.times().elapsed * 1000) if hasattr(os, 'times') else id(text)}.mp3"
            tts.save(filename)
            return filename
        except ImportError:
            return "⚠️ gTTS مو متببت — شغّل: pip install gTTS"
        except Exception as e:
            return f"⚠️ خطأ بالصوت: {str(e)}"

    async def _elevenlabs_tts(self, text, lang):
        """تحويل النص لصوت باستخدام ElevenLabs API"""
        import httpx
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice}"
        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            filename = f"{self.voice_dir}/voice_el_{len(text)}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            raise Exception(f"ElevenLabs error: {response.status_code}")

    def get_status(self):
        """حالة الصوت"""
        has_eleven = "✅" if self.elevenlabs_key else "❌"
        return f"{has_eleven} ElevenLabs | gTTS: متاح"
