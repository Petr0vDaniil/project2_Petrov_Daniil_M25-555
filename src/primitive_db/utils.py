"""Utility functions for database operations."""

import json
from pathlib import Path


def load_metadata(filepath: str) -> dict:
    """Load metadata from JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Save metadata to JSON file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_table_data(table_name: str, data_dir: str = "data") -> list:
    """Load table data from JSON file."""
    filepath = Path(data_dir) / f"{table_name}.json"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_table_data(
    table_name: str,
    data: list,
    data_dir: str = "data"
) -> None:
    """Save table data to JSON file."""
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path(data_dir) / f"{table_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
