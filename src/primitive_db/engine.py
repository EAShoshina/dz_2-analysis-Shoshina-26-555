import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_start_menu() -> None:
    """Выводит приветственное меню при запуске."""
    print("\n***База данных***")
    print("\nФункции:")
    print("<command> create_table <имя_таблицы> "
          "<столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_help() -> None:
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Основной цикл программы."""
    print_start_menu()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        command = args[0]
        cmd_args = args[1:]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            list_tables(metadata)
        elif command == "create_table":
            if len(cmd_args) < 2:
                print("Ошибка: укажите имя таблицы и хотя бы один столбец.")
                continue
            table_name = cmd_args[0]
            columns = cmd_args[1:]
            updated = create_table(metadata, table_name, columns)
            if updated is not metadata:  # если что-то изменилось
                save_metadata(META_FILE, updated)
        elif command == "drop_table":
            if len(cmd_args) != 1:
                print("Ошибка: укажите имя таблицы.")
                continue
            updated = drop_table(metadata, cmd_args[0])
            if updated is not metadata:
                save_metadata(META_FILE, updated)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")