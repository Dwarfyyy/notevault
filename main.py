"""Точка входа приложения NoteVault.

Запуск:
    python main.py [--vault PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="notevault",
        description="NoteVault — личная база знаний в духе Obsidian",
    )
    parser.add_argument(
        "--vault",
        type=Path,
        default=Path(__file__).parent / "examples" / "demo_vault",
        help="путь к хранилищу заметок (по умолчанию — demo_vault)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    vault_path = args.vault.resolve()
    vault_path.mkdir(parents=True, exist_ok=True)

    from notevault.ui.app import run  # импорт здесь, чтобы ядро не требовало GUI

    return run(vault_path)


if __name__ == "__main__":
    sys.exit(main())
