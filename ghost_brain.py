# ============================================================
# Ghost Brain — عقل الشبح
# معالجة الذكاء الاصطناعي
# ============================================================
import json
import httpx
from datetime import datetime
from config import (
    LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL,
    LLM_TEMPERATURE, LLM_MAX_TOKENS, OWNER_NAME, GHOST_NAME
)


class GhostBrain:
    """عقل Ghost — الذكاء الاصطناعي"""

    def __init__(self, memory=None, personality=None):
        self.memory = memory
        self.personality = personality
        self.provider = LLM_PROVIDER
        self.model = LLM_MODEL
        self.api_key = LLM_API_KEY
        self.base_url = LLM_BASE_URL
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS

        # سجلّان منفصلان — كل لغة إلها سجلها الخاص
        # هيك ما بينلخبط أسلوب الفصحى مع اللبناني
        self.conversation_history_ar = []
        self.conversation_history_lb = []

    def set_memory(self, memory):
        """تعيين الذاكرة"""
        self.memory = memory

    def set_personality(self, personality):
        """تعيين الشخصية"""
        self.personality = personality

    def _get_history(self, lang):
        """اختيار السجل الصحيح حسب اللغة"""
        if lang == "lb":
            return self.conversation_history_lb
        return self.conversation_history_ar

    def _build_messages(self, user_message, system_prompt=None,
                        context=None, lang=None):
        """بناء قائمة الرسائل للإرسال"""
        messages = []

        # Prompt النظام
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif self.personality:
            messages.append({
                "role": "system",
                "content": self.personality.get_system_prompt(
                    lang=lang or self.personality.default_lang
                )
            })

        # سياق الذاكرة
        if context:
            messages.append({
                "role": "system",
                "content": f"سياق من الذاكرة:\n{context}"
            })

        # سجل المحادثة — فقط من نفس اللغة (آخر 6 رسائل، أخف وأسرع)
        history = self._get_history(lang)
        recent = history[-6:]
        for msg in recent:
            messages.append(msg)

        # رسالة المستخدم
        messages.append({"role": "user", "content": user_message})

        return messages

    def _get_memory_context(self, query):
        """البحث بالذاكرة عن سياق مرتبط"""
        if not self.memory:
            return ""
        results = self.memory.recall(query, limit=5)
        if not results:
            return ""
        context_lines = []
        for r in results:
            context_lines.append(
                f"- {r['key']}: {r['value']}"
            )
        return "\n".join(context_lines)

    async def think(self, user_message, lang=None, sender_name=None,
                    platform="telegram", system_prompt=None):
        """التفكير — توليد رد"""
        if not self.api_key:
            return "⚠️ ما في مفتاح API — لسّا ما بعرف أحكي!"

        # كشف اللغة فقط لو ما انبعتلناش من غوست كور
        if lang is None and self.personality:
            lang = self.personality.detect_language(user_message)

        # جلب سياق من الذاكرة
        context = self._get_memory_context(user_message)

        # بناء الرسائل
        messages = self._build_messages(
            user_message=user_message,
            system_prompt=system_prompt,
            context=context,
            lang=lang
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]

                # حفظ بالسجل الصحيح حسب اللغة
                history = self._get_history(lang)
                history.append({"role": "user", "content": user_message})
                history.append({"role": "assistant", "content": reply})

                if len(history) > 30:
                    history[:] = history[-30:]

                return reply
            else:
                return f"⚠️ خطأ من LLM: {response.status_code}"

        except Exception as e:
            return f"⚠️ خطأ بالاتصال: {str(e)}"

    def think_sync(self, user_message, lang=None, sender_name=None,
                   platform="telegram", system_prompt=None):
        """نسخة متزامنة من think"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self.think(
                            user_message, lang, sender_name,
                            platform, system_prompt
                        )
                    )
                    return future.result(timeout=60)
            else:
                return loop.run_until_complete(
                    self.think(
                        user_message, lang, sender_name,
                        platform, system_prompt
                    )
                )
        except RuntimeError:
            return asyncio.run(
                self.think(
                    user_message, lang, sender_name,
                    platform, system_prompt
                )
            )

    def clear_history(self):
        """مسح سجل المحادثة"""
        self.conversation_history_ar = []
        self.conversation_history_lb = []
        return "✅ مسحت سجل المحادثة"

    def get_status(self):
        """حالة العقل"""
        has_key = "✅" if self.api_key else "❌"
        total = len(self.conversation_history_ar) + len(self.conversation_history_lb)
        return (
            f"{has_key} API Key | "
            f"Model: {self.model} | "
            f"Messages: {total}"
        )
