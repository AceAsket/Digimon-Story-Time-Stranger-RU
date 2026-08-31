#!/usr/bin/env python3
"""Normalize confirmed story terms across the translated package."""

from __future__ import annotations

from pathlib import Path

from fix_t01_npc_context_v169 import read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "csv" / "patch_text01"

# old text, replacement, exact number present before this pass
REPLACEMENTS: tuple[tuple[str, str, int], ...] = (
    ("Бахусмон", "Вакхмон", 80),
    ("Сайренмон", "Сиренмон", 10),
    ("Зубчатый Лес", "Зубчатый лес", 6),
    ("Космическую Зону", "Космическую область", 1),
    ("Потока", "Течения", 6),
    ("Поток", "Течение", 8),
    ("Дайанамон", "Дианамон", 19),
    ("ГрейсНовамон", "Грейс Новамон", 5),
    ("Тёмное Поле", "Тёмное поле", 9),
    ("Центральному Городу", "Центральному городу", 1),
)


def main() -> None:
    documents: dict[Path, list[list[str]]] = {}
    formats: dict[Path, tuple[str, str]] = {}
    files = sorted(PACKAGE_ROOT.rglob("*.csv"))

    for path in files:
        rows, encoding, mode = read_document(path)
        documents[path] = rows
        formats[path] = (encoding, mode)

    dirty: set[Path] = set()
    total_changed = 0
    for old, new, expected in REPLACEMENTS:
        found = sum(cell.count(old) for rows in documents.values() for row in rows for cell in row)
        if found not in (0, expected):
            raise SystemExit(f"Unexpected occurrence count for {old!r}: {found}, expected {expected} or 0")
        if found == 0:
            print(f"Already current: {old!r} -> {new!r}")
            continue
        changed = 0
        for path, rows in documents.items():
            for row in rows:
                for index, cell in enumerate(row):
                    occurrences = cell.count(old)
                    if not occurrences:
                        continue
                    row[index] = cell.replace(old, new)
                    changed += occurrences
                    dirty.add(path)
        if changed != expected:
            raise SystemExit(f"Replacement count drift for {old!r}: {changed}, expected {expected}")
        total_changed += changed
        print(f"Changed: {old!r} -> {new!r}: {changed}")

    for path in sorted(dirty):
        encoding, mode = formats[path]
        write_document(path, documents[path], encoding, mode)

    print(f"Occurrences changed: {total_changed}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()
