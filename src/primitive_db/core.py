from prettytable import PrettyTable

VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """Создаёт таблицу, добавляет ID:int и возвращает обновлённые метаданные."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    # Проверка типов
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        _, col_type = col.split(":", 1)
        if col_type not in VALID_TYPES:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return metadata

    # Добавляем ID:int в начало
    formatted_columns = [{"name": "ID", "type": "int"}]
    for col in columns:
        name, col_type = col.split(":", 1)
        formatted_columns.append({"name": name, "type": col_type})

    # Создаём копию, чтобы не мутировать исходный словарь
    new_metadata = dict(metadata)
    new_metadata[table_name] = formatted_columns
    cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in formatted_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return new_metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    new_metadata = dict(metadata)
    del new_metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return new_metadata


def list_tables(metadata: dict) -> None:
    """Печатает список всех таблиц."""
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")

def insert(metadata: dict, table_name: str, values: list) -> list:
    """Добавляет запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []

    schema = metadata[table_name]
    # Исключаем ID из проверки (первый столбец)
    expected_cols = schema[1:]

    if len(values) != len(expected_cols):
        print(f"Ошибка: неверное количество значений. Ожидалось {len(expected_cols)}.")
        return []

    # Валидация типов
    for i, (val, col) in enumerate(zip(values, expected_cols)):
        col_type = col["type"]
        if col_type == "int" and not isinstance(val, int):
            print(f"Ошибка: значение для '{col['name']}' должно быть int.")
            return []
        if col_type == "bool" and not isinstance(val, bool):
            print(f"Ошибка: значение для '{col['name']}' должно быть bool.")
            return []

    # Генерация ID и создание записи
    from primitive_db.utils import load_table_data, save_table_data

    table_data = load_table_data(table_name)
    new_id = max([row["ID"] for row in table_data], default=0) + 1

    new_row = {"ID": new_id}
    for val, col in zip(values, expected_cols):
        new_row[col["name"]] = val

    table_data.append(new_row)
    save_table_data(table_name, table_data)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data: list, where_clause: dict = None) -> list:
    """Возвращает отфильтрованные записи."""
    if not where_clause:
        return table_data

    result = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if row.get(key) != val:
                match = False
                break
        if match:
            result.append(row)
    return result


def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Обновляет записи, подходящие под where_clause."""
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if row.get(key) != val:
                match = False
                break
        if match:
            for k, v in set_clause.items():
                if k in row:
                    row[k] = v
    return table_data


def delete(table_data: list, where_clause: dict) -> list:
    """Удаляет записи, подходящие под where_clause."""
    return [
        row
        for row in table_data
        if not all(row.get(k) == v for k, v in where_clause.items())
    ]


def print_table(table_data: list, table_name: str) -> None:
    """Выводит данные в красивом формате с помощью PrettyTable."""
    if not table_data:
        print("Таблица пуста.")
        return

    pt = PrettyTable()
    pt.field_names = list(table_data[0].keys())
    for row in table_data:
        pt.add_row(list(row.values()))
    print(pt)


def table_info(metadata: dict, table_name: str) -> None:
    """Выводит информацию о таблице."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    from primitive_db.utils import load_table_data

    schema = metadata[table_name]
    cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in schema)
    data = load_table_data(table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(data)}")