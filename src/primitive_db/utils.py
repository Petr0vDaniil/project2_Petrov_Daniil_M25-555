"""Utility functions for database operations."""

import json
from pathlib import Path


def load_metadata(filepath: str) -> dict:
    """Load metadata from JSON file.

    Args:
        filepath: Path to the metadata JSON file

    Returns:
        Dictionary with table metadata or empty dict if file not found
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        # Если файл пустой или повреждён
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Save metadata to JSON file.

    Args:
        filepath: Path to save the metadata JSON file
        data: Dictionary with table metadata
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
