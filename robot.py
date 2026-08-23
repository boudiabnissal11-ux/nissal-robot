# robot.py - الجسم - يستعمل عقل Ghost
from ghost_brain import GhostBrain

print("👻 مرحبا! Ghost")
name = input("شو اسمك حبيب؟ ")
print(f"اهلا وسهلا يا {name}!")

brain = GhostBrain()

while True:
    command = input(f"({name}) شو بدك يا {name}؟ رقص / نكتة / ذكرني / احفظ: ")

    if not command.strip():
        continue

    if command == "رقص" or command == "dance":
        print("💃 اه رقص Ghost! Booo! Beep boop! 👻")

    elif command == "نكتة" or command == "joke":
        print("😂 مرة واحد راح عند الحلاق، قالو: قلّلي، قالو: ما بتعرف تحكي من قبل؟")

    elif "احفظ" in command or "شو حفظت" in command or "متذكر" in command or "انسى" in command or "امحي" in command:
        answer = brain.respond(command)
        print(f"🧠 {answer}")

    elif command == "اسمي" or command == "what's your name" or command == "who are you":
        print(f"انا Ghost! السكرتير الشخصي لنصال، وهلا عم احكي مع {name}!")

    elif command == "كيفك" or command == "how are you":
        print(f"تمام كتير! انا منيح يا {name} ❤️")

    elif command == "باي" or command == "bye":
        print(f"باي باي {name}! Ghost راح ينام 😴👻")
        break

    else:
        answer = brain.respond(command)
        print(f"👻 {answer} يا {name}")
