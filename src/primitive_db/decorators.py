"""Decorators for database operations."""

import time
from functools import wraps
from typing import Any, Callable


def handle_db_errors(func: Callable) -> Callable:
    """Decorator to handle database errors gracefully."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            return None, f"Ошибка: Файл не найден. {str(e)}"
        except KeyError as e:
            return None, f"Ошибка: Таблица или столбец {e} не найден."
        except ValueError as e:
            return None, f"Ошибка валидации: {e}"
        except Exception as e:
            return None, f"Произошла непредвиденная ошибка: {type(e).__name__}: {e}"
    return wrapper


def confirm_action(action_name: str) -> Callable:
    """Decorator factory for requesting user confirmation."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirm = input(f'Вы уверены, что хотите выполнить "{action_name}"?'
                            f' [y/n]: ').strip().lower()
            if confirm != 'y':
                return None, "Операция отменена."
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func: Callable) -> Callable:
    """Decorator to measure and log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        elapsed = end - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Factory function that returns a caching function using closure."""
    cache = {}
    
    def cache_result(key: str, value_func: Callable) -> Any:
        """Cache result based on key. If not in cache, compute using value_func."""
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    
    return cache_result
