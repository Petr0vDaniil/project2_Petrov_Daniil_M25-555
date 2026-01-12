"""Core database operations for table management."""

from typing import Optional

VALID_TYPES = {"int", "str", "bool"}
METADATA_FILE = "db_meta.json"


def create_table(
    metadata: dict,
    table_name: str,
    columns: list[str],
) -> tuple[dict, Optional[str]]:
    """Create a new table.

    Args:
        metadata: Current metadata dictionary
        table_name: Name of the table to create
        columns: List of columns in format "name:type"

    Returns:
        Tuple of (updated_metadata, error_message)
        error_message is None if successful
    """
    # Проверка: таблица уже существует?
    if table_name in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" уже существует.'

    # Инициализируем структуру таблицы с ID
    table_structure = {"ID": "int"}

    # Проверяем и добавляем столбцы пользователя
    for column in columns:
        if ":" not in column:
            return metadata, f"Некорректное значение: {column}. Попробуйте снова."

        col_name, col_type = column.split(":", 1)
        col_name = col_name.strip()
        col_type = col_type.strip()

        # Валидация типа
        if col_type not in VALID_TYPES:
            return (
                metadata,
                f"Некорректное значение: {col_type}. Попробуйте снова.",
            )

        # Добавляем столбец
        table_structure[col_name] = col_type

    # Сохраняем таблицу в метаданные
    metadata[table_name] = table_structure

    return metadata, None  # error_message = None значит успех!


def drop_table(metadata: dict, table_name: str) -> tuple[dict, Optional[str]]:
    """Drop (delete) a table.

    Args:
        metadata: Current metadata dictionary
        table_name: Name of the table to drop

    Returns:
        Tuple of (updated_metadata, error_message)
        error_message is None if successful
    """
    # Проверка: таблица существует?
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'

    # Удаляем таблицу
    del metadata[table_name]

    return metadata, None  # error_message = None значит успех!


def list_tables(metadata: dict) -> list[str]:
    """Get list of all table names.

    Args:
        metadata: Current metadata dictionary

    Returns:
        List of table names
    """
    return list(metadata.keys())


def validate_table_name(table_name: str) -> Optional[str]:
    """Validate table name format.

    Args:
        table_name: Name to validate

    Returns:
        Error message if invalid, None if valid
    """
    if not table_name or not table_name.isidentifier():
        return f"Некорректное значение: {table_name}. Попробуйте снова."
    return None
