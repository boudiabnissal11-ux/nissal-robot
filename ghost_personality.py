# ============================================================
# Ghost Personality — شخصية الشبح
# أسلوب نصال — لبناني، فصحى، إنجليزي
# ============================================================
import re
from datetime import datetime
from config import GHOST_PERSONALITY, DEFAULT_LANGUAGE, OWNER_NAME


class GhostPersonality:
    """شخصية Ghost — بيحكي بأسلوب نصال"""

    # علامات لبنانية (عمية) — بالحروف العربية
    LEBANESE_MARKERS = [
        "شو", "ليش", "هيك", "هاد", "هادي", "هول", "هولة",
        "عمية", "يا عمي", "والعافية", "خلص", "طيب", "أوكي",
        "بدك", "بدي", "بتحكي", "بنروح", "شلون", "غشيم",
        "يا نصال", "حبيبي", "يا عمري", "شريكي", "يا سيدي",
        "كيفك", "شو الأخبار", "ممتاز", "تمام", "يا ريت",
        "هلّق", "بعدنا", "عنا", "إلنا", "علينا", "محلى",
        "يا عيني", "وشو", "إمتى", "هون", "هونيك",
    ]

    # علامات لبنانية مكتوبة Arabizi (حروف لاتينية)
    LEBANESE_ARABIZI_MARKERS = [
        "kifak", "kifik", "kifkon", "shu", "shou", "chou",
        "habibi", "habibe", "hbibi", "mnih", "mni7", "mnee7",
        "tamam", "tmam", "khalas", "khallas", "khalass",
        "yalla", "yaala", "yala", "3am", "3ala", "2al", "2alo",
        "3endak", "3andak", "wein", "win", "leish", "laish", "kifak",
        "bade", "badde", "baddi", "bde", "keefak", "keefik",
        "sar", "ma3ak", "ma3ik", "hala", "ahla", "marhaba",
        "shu fi", "chou fi", "3anjad", "akid", "aktar", "kteer",
        "ktir", "maneh", "za3lan", "mabsout", "mabsoot", "yislamo",
        "tfaddal", "tfaddol", "eh", "la2", "laa2", "shakle",
    ]

    # علامات فصحى
    FUSHA_MARKERS = [
        "ماذا", "لماذا", "كيف", "أين", "متى", "من",
        "الذي", "التي", "اللذان", "اللتان",
        "إنّ", "أنّ", "لن", "لم", "قد", "كان",
        "وجب", "ينبغي", "يرجى", "شكراً جزيلاً",
        "السلام عليكم", "أهلاً وسهلاً",
    ]

    # علامات إنجليزي
    ENGLISH_MARKERS = [
        "what", "how", "why", "when", "where", "who",
        "please", "thank", "hello", "hey", "hi",
        "can you", "i want", "i need", "help",
        "task", "meeting", "subscription", "payment",
    ]

    def __init__(self):
        self.personality = GHOST_PERSONALITY
        self.default_lang = DEFAULT_LANGUAGE
        self.learned_style = {}

    def _count_markers(self, text_lower, markers):
        """عدّ العلامات بكلمة كاملة (word boundary) مش substring"""
        count = 0
        for m in markers:
            pattern = r'(?<![a-zA-Z0-9\u0600-\u06FF])' + \
                      re.escape(m.lower()) + \
                      r'(?![a-zA-Z0-9\u0600-\u06FF])'
            if re.search(pattern, text_lower):
                count += 1
        return count

    def detect_language(self, text):
        """كشف لغة النص تلقائياً"""
        text_lower = text.lower()

        # لو نصال حكى — إشارة قوية للبناني
        owner_bonus = 0
        if OWNER_NAME in text or "@NISSALBOUDIAB" in text.upper():
            owner_bonus = 5

        # هل فيه حروف عربية بالنص؟
        has_arabic_script = bool(re.search(r'[\u0600-\u06FF]', text))

        # هل فيه حروف لاتينية متتالية (3+)؟
        has_latin = bool(re.search(r'[a-zA-Z]{3,}', text))

        lb_score = self._count_markers(text_lower, self.LEBANESE_MARKERS) + owner_bonus
        ar_score = self._count_markers(text_lower, self.FUSHA_MARKERS)
        en_score = self._count_markers(text_lower, self.ENGLISH_MARKERS)
        lb_arabizi_score = self._count_markers(text_lower, self.LEBANESE_ARABIZI_MARKERS)

        # الحالة 1: نص مكتوب بحروف عربية
        if has_arabic_script:
            if lb_score == 0 and ar_score == 0:
                return "lb"  # افتراضي لبناني لو مفيش علامات واضحة
            return "lb" if lb_score >= ar_score else "ar"

        # الحالة 2: نص مكتوب بحروف لاتينية فقط (Arabizi أو إنجليزي)
        if has_latin:
            if lb_arabizi_score > 0 and lb_arabizi_score >= en_score:
                return "lb"
            if en_score > 0:
                return "en"
            if owner_bonus > 0:
                return "lb"

        # الحالة 3: ما قدرنا نحسم — رجّح حسب أعلى نقاط
        scores = {"lb": lb_score, "ar": ar_score, "en": en_score}
        detected = max(scores, key=scores.get)

        if scores[detected] == 0:
            return self.default_lang

        return detected

    def get_system_prompt(self, lang=None, sender_name=None,
                          platform="telegram"):
        """بناء prompt النظام حسب اللغة والسياق"""
        if lang is None:
            lang = self.default_lang

        base = self.personality

        # إضافات حسب اللغة
        if lang == "lb":
            lang_instruction = (
                "\n\nمهم جداً: رد فقط باللهجة اللبنانية المحكية (العامية)، "
                "وممنوع تستخدم أي كلمة أو تركيب فصيح متل: (ماذا، لماذا، "
                "أين، الذي، إنّ، لن، لم). "
                "استخدم قواعد اللبناني: "
                "'شو' بدل ماذا، 'ليش' بدل لماذا، 'وين' بدل أين، "
                "'هيدا/هيدي' أو 'هاد/هاي' بدل هذا/هذه، "
                "'ما بعرف' بدل لا أعرف، 'رح' بدل سوف، "
                "'عم ب' للمضارع المستمر (متل: عم بحكي، عم بشتغل)، "
                "'مش' بدل ليس، 'كتير' بدل جداً/كثيراً. "
                "أمثلة على أسلوبك: "
                "'أهلين حبيبي، شو الأخبار؟' / "
                "'تمام يا نصال، خلص ضبطتلك الموضوع' / "
                "'ما تهتم، أنا هون وعم بتابعلك كل شي' / "
                "'يا ريت تعطيني كم تفصيل زيادة كرمال أفهم أكتر'. "
                "خلي جوابك طبيعي متل ما نصال نفسه بيحكي مع صاحبو، "
                "مش متل كتاب أو ترجمة."
            )
        elif lang == "ar":
            lang_instruction = (
                "\n\nمهم: رد بالفصحى. "
                "استخدم لغة عربية فصحى واضحة. "
                "كن مهذباً ومحترماً."
            )
        else:
            lang_instruction = (
                "\n\nImportant: Respond in English. "
                "Be direct, professional, and helpful."
            )

        # إضافات حسب المرسل
        sender_instruction = ""
        if sender_name and sender_name != OWNER_NAME:
            sender_instruction = (
                f"\n\nالمتحدث: {sender_name} — "
                f"ما هو نصال. كن مهذب بس ما تعطي معلومات شخصية."
            )
        elif sender_name == OWNER_NAME:
            sender_instruction = (
                f"\n\nالمتحدث: {OWNER_NAME} — "
                f"هاد صاحبك. عامله باحترام وأخوية."
            )

        # إضافات حسب المنصة
        platform_instruction = ""
        if platform == "whatsapp":
            platform_instruction = (
                "\n\nالمنصة: واتساب — ردود قصيرة ومفيدة."
            )
        elif platform == "phone":
            platform_instruction = (
                "\n\nالمنصة: مكالمة هاتفية — ردود مختصرة وواضحة."
            )

        return base + lang_instruction + sender_instruction + platform_instruction

    def get_greeting(self, lang=None):
        """تحية حسب الوقت واللغة"""
        if lang is None:
            lang = self.default_lang

        hour = datetime.now().hour

        if lang == "lb":
            if 5 <= hour < 12:
                return "صباح الخير حبيبي! ☀️"
            elif 12 <= hour < 18:
                return "مسا النور يا عمي! 🌤️"
            else:
                return "مسا الخير حبيبي! 🌙"
        elif lang == "ar":
            if 5 <= hour < 12:
                return "صباح الخير! ☀️"
            elif 12 <= hour < 18:
                return "مساء النور! 🌤️"
            else:
                return "مساء الخير! 🌙"
        else:
            if 5 <= hour < 12:
                return "Good morning! ☀️"
            elif 12 <= hour < 18:
                return "Good afternoon! 🌤️"
            else:
                return "Good evening! 🌙"

    def get_farewell(self, lang=None):
        """وداع حسب اللغة"""
        if lang is None:
            lang = self.default_lang

        if lang == "lb":
            return "مع السلامة حبيبي! 👻"
        elif lang == "ar":
            return "مع السلامة! 👻"
        else:
            return "Goodbye! 👻"

    def learn_style(self, text, source="owner"):
        """تعلّم أسلوب المستخدم"""
        words = re.findall(r'\b\w+\b', text.lower())
        new_words = [w for w in words if len(w) >= 3]

        for word in new_words[:10]:
            if word not in self.learned_style:
                self.learned_style[word] = {
                    "word": word,
                    "count": 1,
                    "source": source,
                    "learned_at": str(datetime.now())
                }
            else:
                self.learned_style[word]["count"] += 1

        return len(new_words)

    def get_learned_words(self, limit=20):
        """الكلمات اللي تعلّمها"""
        sorted_words = sorted(
            self.learned_style.items(),
            key=lambda x: x[1].get("count", 0),
            reverse=True
        )
        return sorted_words[:limit]

    def get_status(self):
        """حالة الشخصية"""
        return f"✅ شخصية جاهزة — لغة: {self.default_lang}"
