def parse_value(value: str):
    """Парсит строку в int, bool или str."""
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value  # если это не число и не bool, возвращаем как строку


def parse_where(where_str: str) -> dict:
    """Превращает 'age = 28' в {'age': 28}."""
    if not where_str:
        return {}
    parts = where_str.split("=")
    if len(parts) != 2:
        return {}
    col = parts[0].strip()
    val = parse_value(parts[1])
    return {col: val}


def parse_set(set_str: str) -> dict:
    """Превращает 'age = 29' в {'age': 29}."""
    return parse_where(set_str)