"""Engine module for command processing and user interaction."""

import prompt


def welcome() -> None:
    """Display welcome message and start the main loop."""
    print("\nПервая попытка запустить проект!\n")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        command = prompt.string("Введите команду: ")

        if command == "exit":
            print("До свидания!")
            break
        elif command == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print(f"Неизвестная команда: {command}")
