# ghost_brain.py - عقل Ghost - صنع في شوف - للاستاذ نصال
import json, os, re, random
from datetime import datetime

class GhostBrain:
    def __init__(self):
        self.owner = "نصال"
        self.knowledge = {"facts": [], "instructions": []}
        if os.path.exists("ghost_knowledge.json"):
            try:
                with open("ghost_knowledge.json", 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
            except: pass

    def save(self):
        with open("ghost_knowledge.json", 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

    def learn(self, txt):
        entry = {"text": txt, "time": str(datetime.now())}
        if any(x in txt for x in ["اذا حدا", "ذكرني", "لما", "اذا"]):
            self.knowledge["instructions"].append(entry)
        else:
            self.knowledge["facts"].append(entry)
        self.save()
        return f"حفظت: {txt} - مظبوط؟"

    def forget(self, key):
        n=0
        for c in ["facts", "instructions"]:
            b=len(self.knowledge[c])
            self.knowledge[c]=[x for x in self.knowledge[c] if key not in x["text"]]
            n+=b-len(self.knowledge[c])
        self.save()
        return f"انمحت {n} شغلة فيها {key}" if n>0 else f"ما لقيت {key}"

    def recall(self):
        if not self.knowledge["facts"] and not self.knowledge["instructions"]:
            return "بعد ما حفظت شي"
        t="يلي حافظو:\n"
        for f in self.knowledge["facts"][-5:]: t+=f"- {f['text']}\n"
        for f in self.knowledge["instructions"][-5:]: t+=f"- [امر] {f['text']}\n"
        return t

    def respond(self, txt):
        low=txt.lower()
        if "احفظ" in low:
            c=re.sub(r'^(احفظ|احفظ هيدي|ghost احفظ)', '', txt, flags=re.I).strip()
            return self.learn(c) if c else "شو بدك احفظ؟"
        if "انسى" in low or "امحي" in low or "شيل" in low:
            k=re.sub(r'.*(انسى|امحي|شيل)', '', txt, flags=re.I).strip()
            return self.forget(k) if k else "شو بدك انسى؟"
        if "شو حفظت" in low or "شو متذكر" in low:
            return self.recall()
        if len(txt)>4:
            for f in self.knowledge["facts"]:
                if len(f["text"].split())>0 and f["text"].split()[0] in txt:
                    return f["text"] + " [نبرة واثقة]"
            return f"هيدي بدها تأكيد من الاستاذ {self.owner}، خليني اتأكد وبرجعلك بجواب دقيق"
        return f"هلا يا {self.owner} معك Ghost Private"
