import json
import os

from primitive_db.constants import DATA_DIR, JSON_INDENT


def load_metadata(filepath: str) -> dict:
    """Загружает данные из JSON-файла.

    Если файл не найден, возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)


def load_table_data(table_name: str) -> list:
    """Загружает данные таблицы из JSON-файла."""
    filepath = f"{DATA_DIR}/{table_name}.json"
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные таблицы в JSON-файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = f"{DATA_DIR}/{table_name}.json"
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=JSON_INDENT)