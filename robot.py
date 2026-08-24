# ============================================================
# Ghost CLI — الشبح بالسطر
# تشغيل تجريبي من التيرمنال
# ============================================================
import arabic_reshaper
from bidi.algorithm import get_display
from ghost_brain import GhostBrain
from ghost_memory import GhostMemory
from ghost_personality import GhostPersonality


def ar(text):
    """عرض عربي صح بالتيرمنال"""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def main():
    print(ar("👻 Ghost — الشبح"))
    print(ar("المساعد الشخصي لنصال"))
    print()

    # تحضير المكونات
    memory = GhostMemory()
    personality = GhostPersonality()
    brain = GhostBrain(memory=memory, personality=personality)

    # تحقق من API Key
    if not brain.api_key:
        print(ar("⚠️ ما في LLM_API_KEY!"))
        print(ar("ضيف مفتاح OpenAI بملف .env"))
        print("LLM_API_KEY=sk-your-key-here")
        print()
        print(ar("بدون مفتاح Ghost بيحكي ردود بسيطة"))
        print()

    print(ar(f"🧠 العقل: {brain.get_status()}"))
    print(ar(f"💾 الذاكرة: {memory.get_status()}"))
    print(ar(f"🎭 الشخصية: {personality.get_status()}"))
    print()
    print(ar("اكتب 'باي' أو 'bye' للخروج"))
    print()

    name = "نصال"

    while True:
        try:
            cmd = input(f"{name} > ")
        except (EOFError, KeyboardInterrupt):
            print(ar("\nباي يا نصال بشوفك بعدين 👋"))
            break

        if not cmd.strip():
            continue

        if cmd.strip() in ("باي", "bye", "خروج", "exit", "quit"):
            print(ar("باي يا نصال بشوفك بعدين 👋"))
            break

        # كشف اللغة
        lang = personality.detect_language(cmd)

        # تفكير Ghost
        answer = brain.think_sync(
            user_message=cmd,
            lang=lang,
            sender_name=name,
            platform="cli"
        )

        print(f"Ghost > {answer}")
        print()


if __name__ == "__main__":
    main()
