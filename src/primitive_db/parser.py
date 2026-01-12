"""Command parsers for WHERE and SET clauses."""

from typing import Optional


def parse_where_clause(where_str: str) -> Optional[dict]:
    """Parse WHERE clause into a dictionary."""
    if not where_str or "=" not in where_str:
        return None
    
    try:
        parts = where_str.split("=", 1)
        if len(parts) != 2:
            return None
        
        column = parts[0].strip()
        value_str = parts[1].strip()
        value = _convert_value(value_str)
        
        return {column: value}
    except Exception:
        return None


def parse_set_clause(set_str: str) -> Optional[dict]:
    """Parse SET clause into a dictionary."""
    if not set_str:
        return None
    
    try:
        result = {}
        assignments = _split_by_comma(set_str)
        
        for assignment in assignments:
            if "=" not in assignment:
                continue
            
            parts = assignment.split("=", 1)
            if len(parts) != 2:
                continue
            
            column = parts[0].strip()
            value_str = parts[1].strip()
            value = _convert_value(value_str)
            result[column] = value
        
        return result if result else None
    except Exception:
        return None


def _convert_value(value_str: str):
    """Convert string value to appropriate Python type."""
    value_str = value_str.strip()
    
    # Строки в кавычках
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Булевы значения
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False
    
    # Целые числа
    try:
        return int(value_str)
    except ValueError:
        pass
    
    return value_str


def _split_by_comma(s: str) -> list:
    """Split string by comma, but not inside quotes."""
    parts = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in s:
        if char in ('"', "'") and (not in_quotes or char == quote_char):
            if in_quotes and char == quote_char:
                in_quotes = False
                quote_char = None
            elif not in_quotes:
                in_quotes = True
                quote_char = char
            current += char
        elif char == "," and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    
    if current.strip():
        parts.append(current.strip())
    
    return parts
