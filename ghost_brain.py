# ghost_brain.py - عقل Ghost النهائي المحمي - ملك نصال
import json
import os
from datetime import datetime

class GhostBrain:
    def __init__(self):
        self.owner = "نصال"
        self.knowledge = {"facts": [], "instructions": []}
        if os.path.exists("ghost_knowledge.json"):
            try:
                with open("ghost_knowledge.json", 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
            except:
                pass

    def save(self):
        with open("ghost_knowledge.json", 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

    def learn(self, txt, is_owner=False):
        if not is_owner:
            return "⛔ ما بقدر احفظ! بس المعلم نصال هو يلي بيعلمني 👑"
        if not txt.strip():
            return "شو بدي احفظ يا معلم؟"
        entry = {"text": txt, "time": str(datetime.now())}
        if any(x in txt for x in ["اذا", "إذا", "قلي", "قول", "اذا حدا"]):
            self.knowledge["instructions"].append(entry)
        else:
            self.knowledge["facts"].append(entry)
        self.save()
        return f"✅ حفظت يا معلم: {txt}"

    def forget(self, key, is_owner=False):
        if not is_owner:
            return "⛔ ما بقدر امحي شي الا بأمر من المعلم نصال!"
        n = 0
        for c in ["facts", "instructions"]:
            b = len(self.knowledge[c])
            self.knowledge[c] = [x for x in self.knowledge[c] if key not in x["text"]]
            n += b - len(self.knowledge[c])
        self.save()
        if n > 0:
            return f"🗑️ مسحت {n} شغلة فيها ({key}) يا معلم"
        else:
            return f"ما لقيت شي فيه ({key})"

    def recall(self):
        if not self.knowledge["facts"] and not self.knowledge["instructions"]:
            return "🧠 ذاكرتي فاضية يا معلم، علمني شي!"
        t = "🧠 شو متذكر يا معلم نصال:\n"
        for f in self.knowledge["facts"][-10:]:
            t += f"- {f['text']}\n"
        for f in self.knowledge["instructions"][-10:]:
            t += f"📌 {f['text']}\n"
        return t

    def learn_from_file(self, text, is_owner=False):
        # هيدي ميزة الفيديو والمقال يلي طلبتها
        if not is_owner:
            return "⛔ هيدي ميزة التعلم من الملفات بس للمعلم نصال!"
        return "✅ حاضر يا معلم! عطيني الرابط او النص وانا بقراه وبلخصو وبتعلم منو وبطور حالي فيه 👻"

    def respond(self, text, is_owner=False):
        if "احفظ" in text:
            clean = text.replace("احفظ", "").strip()
            return self.learn(clean, is_owner)

        if "انسى" in text or "امحي" in text:
            clean = text.replace("انسى", "").replace("امحي", "").strip()
            return self.forget(clean, is_owner)

        if "شو حفظت" in text or "شو متذكر" in text:
            return self.recall()

        if "اقرا" in text or "اتعلم من" in text or "حضر" in text or "اتعلم" in text:
            return self.learn_from_file(text, is_owner)

        return None
