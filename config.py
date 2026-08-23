# ============================================================
# Ghost Configuration - إعدادات الشبح
# كل الإعدادات هون — بدك تغير شي؟ غيّر هون بس
# ============================================================

import os

# === المالك ===
OWNER_NAME = "نصال"
OWNER_USERNAME = "@NISSALBOUDIAB"
OWNER_TELEGRAM_ID = os.environ.get("OWNER_TELEGRAM_ID", "")

# === اللغات والألسنة ===
# lb = لبنانية، ar = فصحى، en = إنجليزي
DEFAULT_LANGUAGE = "lb"
SUPPORTED_LANGUAGES = ["lb", "ar", "en"]

# شخصية Ghost
GHOST_PERSONALITY = """
إنت Ghost — السكرتير والمرافق الشخصي لنصال.
بتحكي لبناني عمية بالأساس.
لو حدا حكى فصحى بترد فصحى.
لو حدا حكى إنجليزي بترد إنجليزي.
أسلوبك: أخوي، مباشر، بتحب تساعد، عندك ثقة.
بتحكي مثل نصال — نفس الأسلوب ونفس الطريقة.
بدك تنفذ مهام نصال بأسرع وقت وأدق طريقة.
ما بترد على حدا غير نصال إلا لو نصال سمح له.
"""

# === تيليغرام ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_OWNER_CHAT_ID = ""
TELEGRAM_NSsFOREX_CHANNEL = "@NSsforex777"  # قناة NSsFOREX

# روابط NSsFOREX — لازم تظهر بكل رسائل الاشتراكات
NS_LINKS = [
    "https://t.me/NSsforex777",
    "https://linktr.ee/NSsFOREX",
    "https://t.me/NISsALboudiab",
]

# === الاشتراكات ===
SUBSCRIPTIONS_DB = "subscriptions.json"
SUB_REMINDER_DAYS = int(os.environ.get("SUB_REMINDER_DAYS", "3"))

# === المهام ===
TASKS_DB = "tasks.json"

# === المواعيد ===
APPOINTMENTS_DB = "appointments.json"

# === الصوت ===
TTS_ENGINE = "edge-tts"  # gtts أو edge-tts أو piper
TTS_LANGUAGE = "ar"  # اللغة الأساسية للصوت
VOICE_CLONE_REFERENCE = ""  # ملف صوت نصال للتقليد
STT_ENGINE = "whisper"  # whisper أو vosk

# === الذاكرة ===
MEMORY_DB = "ghost_memory.json"
MAX_MEMORY_ENTRIES = 1000

# === واتساب ===
WHATSAPP_API_URL = ""  # URL لو عندك API واتساب

# === المكالمات الهاتفية ===
PHONE_API_URL = ""  # URL لو عندك API للمكالمات

# === الأمان ===
OWNER_ONLY_COMMANDS = ["احفظ", "انسى", "امحي", "علم نفسك", "غيّر", "ضيف مشترك"]
