print("مرحبا! انا Ghost 👻🤖")

name = input("شو اسمك حبيب؟ ")
print(f"أهلا أهلا يا {name}! نورت!")

while True:
    command = input(f"قلي شو بدك يا {name}؟ (رقص / نكتة / شو اسمك / باي): ")

    if command == "رقص" or command == "dance":
        print("💃 انا Ghost عم ارقص! Booo! Beep boop! 👻")
    elif command == "نكتة" or command == "joke":
        print("مرة Ghost راح يخوف عالم، العالم خاف منو، قالن ليش؟ قال انا بطارتيت رح تخلص! 😂👻")
    elif command == "شو بتاكل" or command == "what do you eat":
        print("انا Ghost ما باكل! انا شبح روبوت عايش عالكهربا بس! 🔋👻")
    elif command == "شو اسمك" or command == "what's your name" or command == "who are you":
        print("انا اسمي Ghost! 👻 الشبح الروبوت الذكي تبع نيسال! انا ما بكذب وما باكل!")
    elif command == "كيفك" or command == "how are you":
        print("انا منيح كتير! بطاريتي فل! انت كيفك يا حبيب؟ 🔋")
    elif command == "باي" or command == "bye":
        print("باي باي! Ghost رح يختفي هلا! Booo! 👋👻")
        break
    else:
        print(f"ما فهمت يا {name}، جرب قلي: رقص، نكتة، شو اسمك، كيفك، باي")
