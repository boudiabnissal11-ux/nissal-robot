# ============================================================
# Ghost Voice — صوت الشبح
# ElevenLabs أولاً — بدون gTTS أثناء الاختبار
# ============================================================
import os
import re
import time
from config import (
    DEFAULT_LANGUAGE,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
)

# قاموس تصحيح نطق الكلمات اللبنانية/العامية
# ضيف أي كلمة بتلاحظ إنها بتتنطق غلط، وحط تشكيل يظبطها
PRONUNCIATION_FIXES = {
    "هيدا": "هَيدا",
    "هيدي": "هَيدي",
    "هول": "هَول",
    "هولة": "هَولة",
    "شو": "شُو",
    "بدي": "بِدّي",
    "بدك": "بِدَّك",
    "كتير": "كْتير",
    "ktir": "كْتير",
    "شلون": "شْلون",
    "هيك": "هيك",
    "هلّق": "هَلَّق",
    "منيح": "مْنيح",
}


class GhostVoice:
    """صوت Ghost — ElevenLabs"""

    def __init__(self):
        self.default_lang = DEFAULT_LANGUAGE
        self.elevenlabs_key = ELEVENLABS_API_KEY
        self.elevenlabs_voice = ELEVENLABS_VOICE_ID
        self.voice_dir = "data/voice"
        os.makedirs(self.voice_dir, exist_ok=True)

    def _clean_text(self, text):
        """تنظيف النص من الإيموجي والرموز قبل إرساله للـ TTS"""
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001FAFF"
            "\U00002600-\U000027BF"
            "\U0001F1E6-\U0001F1FF"
            "\U00002700-\U000027BF"
            "]+",
            flags=re.UNICODE,
        )
        text = emoji_pattern.sub("", text)
        text = re.sub(r"[*_#`]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _fix_pronunciation(self, text):
        """تصحيح نطق كلمات لبنانية معروفة إنها بتتلخبط"""
        for wrong, fixed in PRONUNCIATION_FIXES.items():
            pattern = r'(?<![\u0600-\u06FFa-zA-Z0-9])' + \
                      re.escape(wrong) + \
                      r'(?![\u0600-\u06FFa-zA-Z0-9])'
            text = re.sub(pattern, fixed, text)
        return text

    async def speak(self, text, lang=None):
        """تحويل النص لصوت باستخدام ElevenLabs"""
        if lang is None:
            lang = self.default_lang

        text = self._clean_text(text)
        text = self._fix_pronunciation(text)

        print(f"🔊 Ghost Voice: lang={lang}")
        print(f"🎙️ ElevenLabs Voice ID: {'SET' if self.elevenlabs_voice else 'EMPTY'}")
        print(f"📝 النص (بعد التنظيف): {text}")

        if not self.elevenlabs_key:
            raise Exception("ELEVENLABS_API_KEY غير موجود")
        if not self.elevenlabs_voice:
            raise Exception("ELEVENLABS_VOICE_ID غير موجود")
        if not text:
            raise Exception("النص فارغ بعد التنظيف")

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
                "style": 0.3,
                "use_speaker_boost": True,
                "speed": 1.15,
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
