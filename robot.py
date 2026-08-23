import arabic_reshaper
from bidi.algorithm import get_display
from ghost_brain import GhostBrain

def ar(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

print(ar("أهلا يا نصال! Ghost جاهز 👻"))
print(ar("تكلم بالعربي"))

name = "نصال"
brain = GhostBrain()

while True:
    cmd = input(f"{name} > ")
    if cmd == "باي" or cmd == "bye":
        print(ar("باي يا نصال بشوفك بعدين 👋"))
        break

    answer = brain.response(cmd, is_owner=True)
    print(ar(f"Ghost: {answer}"))
