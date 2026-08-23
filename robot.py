print("مرحبا! انا روبوت نيسال 🤖")

name = input("شو اسمك حبيب؟ ")
print(f"أهلا أهلا يا {name}! نورت!")

while True:
    command = input(f"قلي شو بدك يا {name}؟ (رقص / نكتة / شو بتاكل / باي): ")

    if command == "رقص" or command == "dance":
        print("💃 يلا عم ارقص! Beep boop beep!")
    elif command == "نكتة" or command == "joke":
        print("سمع هيدي: مرة روبوت راح عند الحكيم، قالو حكيم حاسس حالي تعبان! قالو الحكيم بسيطة ناقصك تحديث! 😂")
    elif command == "شو بتاكل" or command == "what do you eat":
        print("هههه انا روبوت يا خي ما باكل ولا بشرب! انا عايش عالبطارية والكهربا بس! 🔋🤖")
    elif command == "مين انت" or command == "who are you":
        print("انا روبوت ذكي بس صريح، ما بكذب! انا مصنوع من كود وبتعلم من نيسال!")
    elif command == "باي" or command == "bye":
        print("باي باي يا حبيب! بشوفك بعدين! 👋")
        break
    else:
        print(f"ما فهمت يا {name}، جرب قلي: رقص، نكتة، شو بتاكل، باي")
