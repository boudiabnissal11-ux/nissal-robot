# ============================================================
# Ghost Memory — ذاكرة الشبح
# حفظ، استرجاع، نسيان، تحديث
# ============================================================
import os
import json
from datetime import datetime
from config import MEMORY_DB, MAX_MEMORY_ENTRIES

class GhostMemory:
    """ذاكرة Ghost — كلشي بيتعلمه بيحفظه هون"""

    def __init__(self):
        self.memory_file = MEMORY_DB
        self.max_entries = MAX_MEMORY_ENTRIES
        self.memories = {}
        self.people = {}
        self.messages = []  # سجل الرسائل
        self.load()

    def load(self):
        """تحميل الذاكرة من الملف"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.memories = data.get("memories", {})
                self.people = data.get("people", {})
                self.messages = data.get("messages", [])
            except (json.JSONDecodeError, FileNotFoundError):
                self.memories = {}
                self.people = {}
                self.messages = []
        else:
            # تأكد إن المجلد موجود
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            self.memories = {}
            self.people = {}
            self.messages = []

    def save(self):
        """حفظ الذاكرة للملف"""
        data = {
            "memories": self.memories,
            "people": self.people,
            "messages": self.messages,
            "last_updated": str(datetime.now())
        }
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_message(self, sender, message, platform="telegram",
                     is_owner=False, is_ghost=False):
        """حفظ رسالة بالسجل"""
        entry = {
            "sender": sender,
            "message": message,
            "platform": platform,
            "is_owner": is_owner,
            "is_ghost": is_ghost,
            "timestamp": str(datetime.now())
        }
        self.messages.append(entry)
        # حدّ عدد الرسائل
        if len(self.messages) > 1000:
            self.messages = self.messages[-1000:]
        self.save()
        return entry

    def learn(self, key, value, category="general", source="owner"):
        """تعلّم شي جديد — احفظه"""
        entry = {
            "key": key,
            "value": value,
            "category": category,
            "source": source,
            "learned_at": str(datetime.now()),
            "times_used": 0
        }
        # لو نفس المفتاح موجود — حدّثه
        if key in self.memories:
            entry["times_used"] = self.memories[key].get("times_used", 0)
            self.memories[key] = entry
        else:
            self.memories[key] = entry

        # حدّ عدد الذكريات
        if len(self.memories) > self.max_entries:
            oldest = min(self.memories.items(),
                         key=lambda x: x[1].get("learned_at", ""))
            del self.memories[oldest[0]]

        self.save()
        return entry

    def recall(self, query, category=None, limit=5):
        """استرجاع ذكرى — ابحث بالذاكرة"""
        results = []
        query_lower = query.lower()
        for key, entry in self.memories.items():
            # بحث بالاسم والقيمة
            if (query_lower in key.lower() or
                query_lower in entry.get("value", "").lower()):
                if category and entry.get("category") != category:
                    continue
                entry_copy = entry.copy()
                entry_copy["key"] = key
                results.append(entry_copy)
                if len(results) >= limit:
                    break

        # رتّب حسب الأحدث
        results.sort(
            key=lambda x: x.get("learned_at", ""),
            reverse=True
        )
        return results

    def forget(self, key):
        """انسى شي — امحيه من الذاكرة"""
        if key in self.memories:
            del self.memories[key]
            self.save()
            return True
        return False

    def update(self, key, new_value=None, new_category=None):
        """تحديث ذكرى موجودة"""
        if key not in self.memories:
            return None
        entry = self.memories[key]
        if new_value is not None:
            entry["value"] = new_value
        if new_category is not None:
            entry["category"] = new_category
        entry["updated_at"] = str(datetime.now())
        self.memories[key] = entry
        self.save()
        return entry

    def get_all_categories(self):
        """كل التصنيفات الموجودة"""
        categories = set()
        for entry in self.memories.values():
            categories.add(entry.get("category", "general"))
        return list(categories)

    def get_memory_summary(self):
        """ملخص الذاكرة"""
        categories = {}
        for entry in self.memories.values():
            cat = entry.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "total_memories": len(self.memories),
            "total_people": len(self.people),
            "total_messages": len(self.messages),
            "categories": categories,
            "last_updated": str(datetime.now())
        }

    # === تتبع الناس ===
    def learn_person(self, name, info, platform="unknown"):
        """تعلّم عن شخص جديد"""
        if name not in self.people:
            self.people[name] = {
                "name": name,
                "info": {},
                "platform": platform,
                "first_seen": str(datetime.now()),
                "last_interaction": str(datetime.now()),
                "interaction_count": 0
            }
        # أضف المعلومات
        self.people[name]["info"].update(info)
        self.people[name]["last_interaction"] = str(datetime.now())
        self.people[name]["interaction_count"] = \
            self.people[name].get("interaction_count", 0) + 1
        self.save()
        return self.people[name]

    def get_person(self, name):
        """استرجاع معلومات شخص"""
        return self.people.get(name, None)

    def recall_person(self, query, limit=5):
        """بحث عن شخص"""
        results = []
        query_lower = query.lower()
        for name, person in self.people.items():
            if query_lower in name.lower():
                results.append(person)
                if len(results) >= limit:
                    break
        return results

    def forget_person(self, name):
        """نسيت شخص"""
        if name in self.people:
            del self.people[name]
            self.save()
            return True
        return False

    def get_status(self):
        """حالة الذاكرة"""
        return f"✅ {len(self.memories)} ذكرى | {len(self.people)} شخص | {len(self.messages)} رسالة"
