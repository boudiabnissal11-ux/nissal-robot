print("Hello! I am Nissal Robot 🤖")

name = input("What is your name? ")
print(f"Nice to meet you {name}!")

# Robot brain
while True:
    command = input("Tell me what to do (dance/joke/bye): ")
    
    if command == "dance":
        print("💃🕺 Beep boop I am dancing!")
    elif command == "joke":
        print("Why did the robot go to school? Because his battery was low! 😂")
    elif command == "bye":
        print("Bye bye! See you later! 👋")
        break
    else:
        print("I don't understand, try again!")
