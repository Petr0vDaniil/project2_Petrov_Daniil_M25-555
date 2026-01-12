"""Core database functionality."""

from typing import Optional

from src.primitive_db.utils import save_metadata

METADATA_FILE = "db_meta.json"


def create_table(metadata: dict, table_name: str, columns_str: list) -> Optional[str]:
    """Create a new table."""
    error = validate_table_name(table_name)
    if error:
        return error
    
    if table_name in metadata:
        return f'Ошибка: Таблица "{table_name}" уже существует.'
    
    columns = {"ID": "int"}
    
    for col_def in columns_str:
        if ":" not in col_def:
            return f'Ошибка: Неправильный формат столбца "{col_def}". Используй "имя:тип".'
        
        col_name, col_type = col_def.split(":", 1)
        col_name = col_name.strip()
        col_type = col_type.strip().lower()
        
        if not col_name:
            return "Ошибка: Имя столбца не может быть пустым."
        
        if col_type not in ("int", "str", "bool"):
            return f'Ошибка: Неподдерживаемый тип "{col_type}". Используй int, str или bool.'
        
        if col_name == "ID":
            return 'Ошибка: Столбец "ID" зарезервирован.'
        
        columns[col_name] = col_type
    
    metadata[table_name] = columns
    save_metadata(METADATA_FILE, metadata)
    return None


def drop_table(metadata: dict, table_name: str) -> Optional[str]:
    """Drop a table."""
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    save_metadata(METADATA_FILE, metadata)
    return None


def validate_table_name(table_name: str) -> Optional[str]:
    """Validate table name."""
    if not table_name:
        return "Ошибка: Имя таблицы не может быть пустым."
    
    if not table_name.isidentifier():
        return f'Ошибка: "{table_name}" содержит недопустимые символы.'
    
    return None


def insert(
    metadata: dict,
    table_name: str,
    values: list,
    table_data: list,
) -> tuple[list, Optional[str]]:
    """Insert a new record into a table."""
    if table_name not in metadata:
        return table_data, f'Ошибка: Таблица "{table_name}" не существует.'
    
    table_columns = metadata[table_name]
    expected_count = len(table_columns) - 1
    
    if len(values) != expected_count:
        return (
            table_data,
            f"Ошибка: ожидается {expected_count} значений, получено {len(values)}.",
        )
    
    column_names = [k for k in table_columns.keys() if k != "ID"]
    column_types = [table_columns[k] for k in column_names]
    
    for value, expected_type in zip(values, column_types):
        error = _validate_value_type(value, expected_type)
        if error:
            return table_data, error
    
    if table_data:
        new_id = max(record["ID"] for record in table_data) + 1
    else:
        new_id = 1
    
    new_record = {"ID": new_id}
    for column_name, value in zip(column_names, values):
        new_record[column_name] = value
    
    table_data.append(new_record)
    return table_data, None


def select(
    table_data: list,
    where_clause: Optional[dict] = None,
) -> list:
    """Select records from table data."""
    if where_clause is None:
        return table_data
    
    result = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        if match:
            result.append(record)
    
    return result


def update(
    table_data: list,
    set_clause: dict,
    where_clause: dict,
) -> tuple[list, Optional[str]]:
    """Update records in table data."""
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        
        if match:
            for column, value in set_clause.items():
                if column != "ID" and column in record:
                    record[column] = value
    
    return table_data, None


def delete(
    table_data: list,
    where_clause: dict,
) -> tuple[list, Optional[str]]:
    """Delete records from table data."""
    initial_count = len(table_data)
    
    filtered_data = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        if not match:
            filtered_data.append(record)
    
    return filtered_data, None


def get_table_info(
    metadata: dict,
    table_name: str,
    table_data: list,
) -> Optional[str]:
    """Get information about a table."""
    if table_name not in metadata:
        return None
    
    columns_str = ", ".join(
        f"{k}:{v}" for k, v in metadata[table_name].items()
    )
    record_count = len(table_data)
    
    info = f"""Таблица: {table_name}
Столбцы: {columns_str}
Количество записей: {record_count}"""
    
    return info


def _validate_value_type(value, expected_type: str) -> Optional[str]:
    """Validate that value matches expected type."""
    if expected_type == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            return f'Ошибка: ожидается тип int, получено {type(value).__name__}.'
    elif expected_type == "str":
        if not isinstance(value, str):
            return f'Ошибка: ожидается тип str, получено {type(value).__name__}.'
    elif expected_type == "bool":
        if not isinstance(value, bool):
            return f'Ошибка: ожидается тип bool, получено {type(value).__name__}.'
    
    return None
