import shlex

import prompt

from primitive_db import core
from primitive_db.constants import META_FILE
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_set, parse_value, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

cache_result = create_cacher()


def clear_cache_for_table(table_name: str) -> None:
    """Очищает кэш для конкретной таблицы (если мы её изменили)."""
    # Ключи кэша имеют вид "users_{'age': 28}" или "users_{}".
    # Мы не можем напрямую удалить из замыкания, но можем пересоздать кэш.
    global cache_result
    cache_result = create_cacher()


def print_help() -> None:
    """Prints the help message for the current mode."""
    print("\n***База данных***")
    print("\nФункции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("<command> insert into <имя> values (<значение1>, ...) - создать запись")
    print("<command> select from <имя> - прочитать все записи")
    print("<command> select from <имя> where <столбец> = <значение> "
          "- прочитать по условию")
    print("<command> update <имя> set <столбец> = <значение> where ... - обновить")
    print("<command> delete from <имя> where <столбец> = <значение> - удалить")
    print("<command> info <имя> - вывести информацию")
    print("\nОбщие команды:")
    print("<command> exit - выход")
    print("<command> help - справка\n")


def run() -> None:
    """Основной цикл программы."""
    print_help()
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

        command = args[0].lower()
        cmd_args = args[1:]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        # --- Управление таблицами ---
        elif command == "list_tables":
            core.list_tables(metadata)
        elif command == "create_table":
            if len(cmd_args) < 2:
                print("Ошибка: укажите имя таблицы и хотя бы один столбец.")
                continue
            table_name = cmd_args[0]
            columns = cmd_args[1:]
            updated = core.create_table(metadata, table_name, columns)
            save_metadata(META_FILE, updated)
        elif command == "drop_table":
            if len(cmd_args) != 1:
                print("Ошибка: укажите имя таблицы.")
                continue
            updated = core.drop_table(metadata, cmd_args[0])
            if updated is not None:
                save_metadata(META_FILE, updated)
                clear_cache_for_table(cmd_args[0])
        # --- CRUD ---
        elif command == "info":
            if len(args) != 2:
                print("Ошибка: укажите имя таблицы.")
                continue
            core.table_info(metadata, args[1])
        elif command == "insert":
            if (
                len(args) < 5
                or args[1].lower() != "into"
                or args[3].lower() != "values"
            ):
                print("Ошибка синтаксиса insert.")
                continue
            table_name = args[2]
            raw_values = " ".join(args[4:]).strip("()")
            values = [parse_value(v) for v in raw_values.split(",")]
            core.insert(metadata, table_name, values)
            clear_cache_for_table(table_name)
        elif command == "select":
            if len(args) < 3 or args[1].lower() != "from":
                print("Ошибка синтаксиса select.")
                continue
            table_name = args[2]
            where = {}
            if len(args) > 3 and args[3].lower() == "where":
                where = parse_where(" ".join(args[4:]))

            # Ключ кэша — это уникальное сочетание таблицы и условия
            cache_key = f"{table_name}_{where}"

            def fetch_data(t_name: str = table_name, w_clause: dict = where):
                data = load_table_data(t_name)
                return core.select(data, w_clause)

            result = cache_result(cache_key, fetch_data)
            core.print_table(result, table_name)
        elif command == "update":
            if len(args) < 6 or args[2].lower() != "set" or "where" not in args:
                print("Ошибка синтаксиса update.")
                continue
            table_name = args[1]
            where_idx = args.index("where")
            set_clause = parse_set(" ".join(args[3:where_idx]))
            where_clause = parse_where(" ".join(args[where_idx + 1:]))

            data = load_table_data(table_name)
            updated_data = core.update(data, set_clause, where_clause)
            save_table_data(table_name, updated_data)
            clear_cache_for_table(table_name)
            print(f'Записи в таблице "{table_name}" обновлены.')
        elif command == "delete":
            if (
                len(args) < 6
                or args[1].lower() != "from"
                or args[3].lower() != "where"
            ):
                print("Ошибка синтаксиса delete.")
                continue
            table_name = args[2]
            where_clause = parse_where(" ".join(args[4:]))

            data = load_table_data(table_name)
            updated_data = core.delete(data, where_clause)
            if updated_data is not None:
                save_table_data(table_name, updated_data)
                clear_cache_for_table(table_name)
                print(f'Записи из таблицы "{table_name}" удалены.')