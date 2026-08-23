# robot.py - جسم Ghost - مربوط بالعقل المحمي
from ghost_brain import GhostBrain

print("👻 مرحبا! Ghost اشتغل")
name = input("شو اسمك حبيب؟ ")

# هون منحدد اذا انت المالك ولا لا
is_owner = False
if "نصال" in name or "nissal" in name.lower() or "nصال" in name:
    is_owner = True
    print(f"👑 اهلا وسهلا بالمعلم {name}! كل الصلاحيات مفتوحة الك!")
else:
    print(f"اهلا وسهلا يا {name}! فيك تحكي معي بس الذاكرة بس للمعلم نصال 👑")

brain = GhostBrain()

while True:
    command = input(f"({name}) > ")

    if not command.strip():
        continue

    if command == "رقص" or command == "dance":
        print("💃 Booo! Ghost عم يرقص! 👻")

    elif command == "نكتة" or command == "joke":
        print("😂 مرة واحد راح عند الحلاق، قالو قلّلي، قالو ما بتعرف تحكي من قبل؟")

    elif command == "باي" or command == "bye":
        print(f"باي باي {name}! 😴👻")
        break

    else:
        answer = brain.respond(command, is_owner=is_owner)
        if answer:
            print(answer)
        else:
            # دردشة عادية
            if is_owner:
                print(f"👻 فهمت يا معلم {name} - {command}")
            else:
                print(f"👻 اهلا يا {name} - انا Ghost، سكرتير المعلم نصال!")
