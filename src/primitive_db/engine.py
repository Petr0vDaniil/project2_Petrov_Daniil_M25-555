"""Engine module for command processing and user interaction."""

import shlex

from src.primitive_db import core
from src.primitive_db.utils import load_metadata, save_metadata


def print_help() -> None:
    """Print help message for database commands."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Main database loop."""
    print("\n***База данных***\n")
    print_help()

    while True:
        # Загружаем актуальные метаданные
        metadata = load_metadata(core.METADATA_FILE)

        # Запрашиваем команду у пользователя
        try:
            user_input = input(">>>Введите команду: ").strip()
        except EOFError:
            # Ctrl+D
            print("До свидания!")
            break

        if not user_input:
            continue

        # Парсим команду и аргументы
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0].lower()

        # Обработка команд
        if command == "exit":
            print("До свидания!")
            break

        elif command == "help":
            print_help()

        elif command == "create_table":
            if len(args) < 2:
                print(
                    "Функция create_table требует имя таблицы и столбцы. "
                    "Попробуйте снова."
                )
                continue

            table_name = args[1]  # Это строка
            columns = args[2:] if len(args) > 2 else []  # Это список строк

            # Валидация имени таблицы
            error = core.validate_table_name(table_name)
            if error:
                print(error)
                continue

            # Создание таблицы
            metadata, error = core.create_table(metadata, table_name, columns)

            if error:
                print(error)
            else:
                columns_str = ", ".join(
                    f"{k}:{v}" for k, v in metadata[table_name].items()
                )
                print(
                    f'Таблица "{table_name}" успешно создана со столбцами: '
                    f"{columns_str}"
                )
                save_metadata(core.METADATA_FILE, metadata)

        elif command == "drop_table":
            if len(args) < 2:
                print("Функция drop_table требует имя таблицы. Попробуйте снова.")
                continue

            table_name = args[1]  # Это строка

            # Удаление таблицы
            metadata, error = core.drop_table(metadata, table_name)

            if error:
                print(error)
            else:
                print(f'Таблица "{table_name}" успешно удалена.')
                save_metadata(core.METADATA_FILE, metadata)

        elif command == "list_tables":
            tables = core.list_tables(metadata)

            if not tables:
                print("Нет созданных таблиц.")
            else:
                for table in tables:
                    print(f"- {table}")

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
