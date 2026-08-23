print("Hello! مرحبا! I am Nissal Robot 🤖")

name = input("What is your name? شو اسمك؟ ")
print(f"Nice to meet you {name}! تشرفت بمعرفتك!")

while True:
    command = input("Tell me what to do (dance-رقص / joke-نكتة / bye-باي): ")
    
    if command == "dance" or command == "رقص":
        print("💃🕺 Beep boop! عم ارقص! I am dancing!")
    elif command == "joke" or command == "نكتة":
        print("Why did the robot go to school? ليش الروبوت راح عالمدرسة؟ Because his battery was low! لأنو بطاريتو ضعيفة! 😂")
    elif command == "bye" or command == "باي":
        print("Bye bye! باي باي! See you later! 👋")
        break
    else:
        print("I don't understand / ما فهمت! Try رقص or dance!")
