"""Engine module for command processing and user interaction."""

import shlex

from prettytable import PrettyTable

from src.primitive_db import core, parser
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_table_data,
)


def print_help() -> None:
    """Print help message for database commands."""
    print("\n***Управление таблицами***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> ... - создать таблицу"
    )
    print("<command> list_tables - показать все таблицы")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> [where "
        "<столбец> = <значение>] - прочитать записи"
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = "
        "<значение> where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where "
        "<столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    
    print("\n***Общие команды***")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Main database loop."""
    print("\n***База данных***\n")
    print_help()
    
    while True:
        metadata = load_metadata(core.METADATA_FILE)
        
        try:
            user_input = input(">>>Введите команду: ").strip()
        except EOFError:
            print("До свидания!")
            break
        
        if not user_input:
            continue
        
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        
        if not args:
            continue
        
        command = args[0].lower()
        
        if command == "exit":
            print("До свидания!")
            break
        
        elif command == "help":
            print_help()
        
        elif command == "create_table":
            if len(args) < 3:
                print("Синтаксис: create_table <имя_таблицы> <столбец1:тип> ...")
                continue
            
            table_name = args[1]
            columns_str = args[2:]
            
            error = core.create_table(metadata, table_name, columns_str)
            if error:
                print(error)
            else:
                col_display = ", ".join(
                    f"{k}:{v}" for k, v in metadata[table_name].items()
                )
                print(f'Таблица "{table_name}" успешно создана со столбцами:'
                      f' {col_display}')
        
        elif command == "list_tables":
            tables = list(metadata.keys())
            if not tables:
                print("Нет таблиц.")
            else:
                for table_name in tables:
                    print(f"- {table_name}")
        
        elif command == "drop_table":
            if len(args) < 2:
                print("Синтаксис: drop_table <имя_таблицы>")
                continue
            
            table_name = args[1]
            result = core.drop_table(metadata, table_name)
            if isinstance(result, tuple):
                _, error = result
                if error:
                    print(error)
                else:
                    print(f'Таблица "{table_name}" успешно удалена.')
            elif result:
                print(result)
            else:
                print(f'Таблица "{table_name}" успешно удалена.')
        
        elif command == "info":
            if len(args) < 2:
                print("Функция info требует имя таблицы. Попробуйте снова.")
                continue
            
            table_name = args[1]
            table_data = load_table_data(table_name)
            info = core.get_table_info(metadata, table_name, table_data)
            
            if info is None:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
            else:
                print(info)
        
        elif command == "insert":
            if len(args) < 4 or args[1].lower() != "into":
                print("Синтаксис: insert into <таблица> values (<значение1>,"
                      " <значение2>, ...)")
                continue
            
            table_name = args[2]
            
            if args[3].lower() != "values":
                print("Синтаксис: insert into <таблица> values (<значение1>,"
                      " <значение2>, ...)")
                continue
            
            values_str = " ".join(args[4:])
            values = _parse_values(values_str)
            
            if values is None:
                print("Ошибка: некорректный формат значений.")
                continue
            
            table_data = load_table_data(table_name)
            result = core.insert(metadata, table_name, values, table_data)
            
            if isinstance(result, tuple):
                table_data, error = result
                if error:
                    print(error)
                else:
                    last_id = table_data[-1]["ID"]
                    print(f'Запись с ID={last_id} успешно добавлена в таблицу'
                          f' "{table_name}".')
                    save_table_data(table_name, table_data)
        
        elif command == "select":
            if len(args) < 3 or args[1].lower() != "from":
                print("Синтаксис: select from <таблица> [where условие]")
                continue
            
            table_name = args[2]
            where_clause = None
            
            if len(args) > 3 and args[3].lower() == "where":
                where_str = " ".join(args[4:])
                where_clause = parser.parse_where_clause(where_str)
                
                if where_clause is None:
                    print("Ошибка: некорректное условие WHERE. Формат: column"
                          " = value")
                    continue
            
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = load_table_data(table_name)
            result = core.select(table_data, where_clause)
            
            if isinstance(result, tuple):
                selected, error = result
                if error:
                    print(error)
                else:
                    _print_table(metadata[table_name], selected)
            else:
                _print_table(metadata[table_name], result)
        
        elif command == "update":
            if len(args) < 4:
                print("Синтаксис: update <таблица> set <столбец> = <значение>"
                      " where <условие>")
                continue
            
            table_name = args[1]
            
            if args[2].lower() != "set":
                print("Синтаксис: update <таблица> set <столбец> = <значение>"
                      " where <условие>")
                continue
            
            where_idx = None
            for i, arg in enumerate(args):
                if arg.lower() == "where":
                    where_idx = i
                    break
            
            if where_idx is None:
                print("Ошибка: требуется условие WHERE")
                continue
            
            set_str = " ".join(args[3:where_idx])
            where_str = " ".join(args[where_idx + 1:])
            
            set_clause = parser.parse_set_clause(set_str)
            where_clause = parser.parse_where_clause(where_str)
            
            if set_clause is None or where_clause is None:
                print("Ошибка: некорректный формат SET или WHERE")
                continue
            
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = load_table_data(table_name)
            result = core.update(table_data, set_clause, where_clause)
            
            if isinstance(result, tuple):
                table_data, error = result
                if error:
                    print(error)
                else:
                    matching = core.select(table_data, where_clause)
                    if isinstance(matching, tuple):
                        matching, _ = matching
                    for record in matching:
                        print(f'Запись с ID={record["ID"]} в таблице "{table_name}"'
                              f' успешно обновлена.')
                    save_table_data(table_name, table_data)
        
        elif command == "delete":
            if len(args) < 4 or args[1].lower() != "from":
                print("Синтаксис: delete from <таблица> where <условие>")
                continue
            
            table_name = args[2]
            
            if args[3].lower() != "where":
                print("Синтаксис: delete from <таблица> where <условие>")
                continue
            
            where_str = " ".join(args[4:])
            where_clause = parser.parse_where_clause(where_str)
            
            if where_clause is None:
                print("Ошибка: некорректное условие WHERE")
                continue
            
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = load_table_data(table_name)
            to_delete = core.select(table_data, where_clause)
            if isinstance(to_delete, tuple):
                to_delete, _ = to_delete
            
            result = core.delete(table_data, where_clause)
            
            if isinstance(result, tuple):
                table_data, error = result
                if error:
                    print(error)
                else:
                    for record in to_delete:
                        print(f'Запись с ID={record["ID"]} успешно удалена из'
                              f' таблицы "{table_name}".')
                    save_table_data(table_name, table_data)
        
        else:
            print(f"Функции {command} нет. Попробуйте снова.")


def _parse_values(values_str: str):
    """Parse values from string like '(val1, val2, val3)'."""
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]
    
    parts = parser._split_by_comma(values_str)
    
    if not parts:
        return None
    
    values = []
    for part in parts:
        value = parser._convert_value(part)
        values.append(value)
    
    return values


def _print_table(columns_dict: dict, records: list) -> None:
    """Print records as a formatted table using PrettyTable."""
    table = PrettyTable()
    table.field_names = list(columns_dict.keys())
    
    for record in records:
        row = [record.get(col, "") for col in columns_dict.keys()]
        table.add_row(row)
    
    print()
    print(table)
    print()
