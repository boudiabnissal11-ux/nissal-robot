# ============================================================
# Ghost Brain — دماغ الشبح
# الذكاء الاصطناعي — الردود والتفكير
# ============================================================

import os
import json
import httpx
import logging
from datetime import datetime
from config import (
    GHOST_PERSONALITY, DEFAULT_LANGUAGE, OWNER_NAME,
    LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
)

logger = logging.getLogger(__name__)

try:
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "1000"))
except (ValueError, TypeError):
    LLM_BASE_URL = "https://api.openai.com/v1"
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 1000


class GhostBrain:
    """دماغ Ghost — الذكاء الاصطناعي"""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.base_url = LLM_BASE_URL
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS
        self.conversation_history = []
        self.max_history = 50
        self.personality = None
        self.memory = None

    def set_personality(self, personality):
        """ربط الشخصية"""
        self.personality = personality

    def set_memory(self, memory):
        """ربط الذاكرة"""
        self.memory = memory

    def _build_context(self, sender_name=None, platform="telegram",
                       lang=None):
        """بناء السياق الكامل للرد"""
        context_parts = []

        # شخصية
        if self.personality:
            system_prompt = self.personality.get_system_prompt(
                lang=lang, sender_name=sender_name,
                platform=platform
            )
            context_parts.append(
                {"role": "system", "content": system_prompt}
            )
        else:
            context_parts.append(
                {"role": "system", "content": GHOST_PERSONALITY}
            )

        # ذاكرة ذات صلة
        if self.memory and sender_name:
            person_info = self.memory.get_person(sender_name)
            if person_info:
                info_str = json.dumps(person_info.get("info", {}),
                                      ensure_ascii=False)
                context_parts.append({
                    "role": "system",
                    "content": f"معلومات عن {sender_name}: {info_str}"
                })

        # تاريخ المحادثة
        context_parts.extend(self.conversation_history)

        return context_parts

    def think(self, message, sender_name=None, platform="telegram",
              lang=None):
        """التفكير والرد"""
        # كشف اللغة تلقائياً
        if self.personality and lang is None:
            lang = self.personality.detect_language(message)

        # بناء السياق
        context = self._build_context(
            sender_name=sender_name,
            platform=platform,
            lang=lang
        )

        # إضافة رسالة المستخدم
        context.append({"role": "user", "content": message})

        # حفظ بالتاريخ
        self.conversation_history.append(
            {"role": "user", "content": message}
        )

        # طلب الرد من AI
        if self.api_key:
            response = self._call_api(context)
        else:
            response = self._fallback_response(message, lang)

        # حفظ الرد بالتاريخ
        self.conversation_history.append(
            {"role": "assistant", "content": response}
        )

        # حدّ التاريخ
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = \
                self.conversation_history[-self.max_history * 2:]

        # تعلّم من المحادثة
        if sender_name == OWNER_NAME and self.memory:
            self._learn_from_owner(message, response)

        return response

    def _call_api(self, messages):
        """استدعاء API الذكاء الاصطناعي"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }

            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ API HTTP Error: {e}")
            return self._fallback_response(
                messages[-1]["content"], None
            )
        except httpx.TimeoutException:
            logger.error("❌ API Timeout")
            return "⏳ أخد وقت بالرد... جرب بعد شوي."
        except Exception as e:
            logger.error(f"❌ API Error: {e}")
            return self._fallback_response(
                messages[-1]["content"], None
            )

    def _fallback_response(self, message, lang):
        """رد احتياطي — بدون API"""
        if lang is None:
            lang = DEFAULT_LANGUAGE

        message_lower = message.lower()

        if lang == "lb":
            if any(w in message_lower for w in
                   ["أهلا", "هلا", "شلونك", "كيفك"]):
                return "أهلا حبيبي! شو الأخبار؟ كيف بقدر ساعدك؟ 👻"
            elif any(w in message_lower for w in
                     ["شكرا", "ممتاز", "تمام"]):
                return "عافية حبيبي! أي شي بدك إياه بقولي. 👻"
            elif any(w in message_lower for w in
                     ["مساعدة", "ساعدني", "شو بتعرف"]):
                return ("أنا Ghost — شبحك الشخصي! بقدر أساعدك بـ:\n"
                        "📋 المهام\n📅 المواعيد\n👥 الاشتراكات\n"
                        "💳 الدفعات\n🧠 الذواكر\nقللي شو بدك! 👻")
            else:
                return ("حبيبي، للحين ما عندي اتصال بالذكاء الاصطناعي. "
                        "ضيف OPENAI_API_KEY بملف .env وبشتغل غشيم! 👻")

        elif lang == "ar":
            if any(w in message_lower for w in
                   ["مرحبا", "أهلاً", "السلام"]):
                return "مرحباً! كيف يمكنني مساعدتك؟ 👻"
            else:
                return ("عذراً، لا يتوفر لدي اتصال بالذكاء الاصطناعي حالياً. "
                        "يُرجى إضافة OPENAI_API_KEY في ملف .env 👻")
        else:
            if any(w in message_lower for w in
                   ["hello", "hi", "hey"]):
                return "Hello! How can I help you? 👻"
            else:
                return ("Sorry, I don't have AI connection right now. "
                        "Add OPENAI_API_KEY to .env file 👻")

    def _learn_from_owner(self, message, response):
        """تعلّم من محادثة المالك"""
        # لو المالك علّمه شي
        learn_keywords = ["اعرف", "تعلّم", "احفظ", "ذكر",
                          "remember", "learn", "save"]
        message_lower = message.lower()

        if any(kw in message_lower for kw in learn_keywords):
            if self.memory:
                self.memory.learn(
                    key=f"learned_{datetime.now().strftime('%Y%m%d%H%M')}",
                    value=message,
                    category="learned_from_owner",
                    source="owner"
                )

    def clear_history(self):
        """مسح تاريخ المحادثة"""
        self.conversation_history = []

    def get_brain_status(self):
        """حالة الدماغ"""
        has_api = bool(self.api_key)
        history_len = len(self.conversation_history)

        if has_api:
            return f"🧠 متصل — {self.model} — {history_len} رسالة"
        else:
            return f"🧠 بدون API — ردود محلية — {history_len} رسالة"
