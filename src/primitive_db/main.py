#!/usr/bin/env python3
"""Entry point for the primitive_db application."""

from src.primitive_db.engine import welcome


def main() -> None:
    """Main entry point of the application."""
    welcome()


if __name__ == "__main__":
    main()
