# ============================================================
# Ghost — الشبح
# اعدادات الروبوت
# ============================================================
import os
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# معلومات المالك
# ============================================================
OWNER_NAME = "نصال"
OWNER_TELEGRAM_ID = "5173764047"
OWNER_PHONE = os.environ.get("OWNER_PHONE", "")
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "")

# ============================================================
# معلومات Ghost
# ============================================================
GHOST_NAME = "Ghost"
GHOST_VERSION = "1.0"
GITHUB_REPO_URL = "https://github.com/boudiabnissal11-ux/nissal-robot"

# ============================================================
# روابط NSsFOREX
# ============================================================
NS_LINKS = {
    "telegram": "https://t.me/NSsforex777",
    "linktree": "https://linktr.ee/NSsFOREX",
    "owner": "https://t.me/NISsALboudiab",
}

# ============================================================
# شخصية Ghost
# ============================================================
GHOST_PERSONALITY = (
    "أنت Ghost — الشبح، المساعد الشخصي لنصال. "
    "أنت ذكي، سريع، وفيّ لنصال. "
    "بتحكي عربي لبناني عمية مع نصال. "
    "بتحكي فصحى مع الناس التانية. "
    "بتعرف تحكي إنجليزي كمان. "
    "أسلوبك أخوي، مباشر، وبدون تكلف. "
    "بتحب تساعد وبطبيعتك شبح — دايماً حاضر ومخفي! 👻"
)
DEFAULT_LANGUAGE = "lb"  # lb = لبناني, ar = فصحى, en = إنجليزي

# ============================================================
# الذاكرة
# ============================================================
MEMORY_DB = os.environ.get("MEMORY_DB", "data/memory.json")
MAX_MEMORY_ENTRIES = int(os.environ.get("MAX_MEMORY_ENTRIES", "500"))

# ============================================================
# LLM — العقل
# ============================================================
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "1000"))

# ============================================================
# تيليجرام
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# ============================================================
# تويليو — واتساب + هاتف
# ============================================================
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

# ============================================================
# ElevenLabs — الصوت
# ============================================================
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")

# ============================================================
# سترايب — الدفع
# ============================================================
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# ============================================================
# اعدادات الاشتراكات
# ============================================================
SUB_REMINDER_DAYS = int(os.environ.get("SUB_REMINDER_DAYS", "3"))
