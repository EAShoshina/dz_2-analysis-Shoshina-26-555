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