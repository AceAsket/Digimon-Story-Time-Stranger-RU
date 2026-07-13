#!/usr/bin/env python3
"""Fix the source-confirmed second block of example-calque dialogue tails."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv",
     "ofa_001_4_reaction_char_OPHANIMON", 2,
     "810de8ec5f120a641907e3c79ab9c4bae8f4011d746f8dde458b05cbbecb26f2",
     "Я здесь не случайно: мне предстоит за чем-то наблюдать\n"
     "и чего-то добиться."),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv",
     "pega_001_4_reaction_char_PEGASMON", 2,
     "8ee5f53817e7b25ac771c9d2c7cf16e6b4b994a77df3a8623392c2ac48fcd823",
     "Уверяю тебя, это рефлекс.\n"
     "Но рядом с тобой он, возможно, и не сработает?"),
    ("patch_text01", "message/m100.mbe/000_Sheet1.csv", "m100_030_180", 2,
     "cd4be3628ce4d37dd239e06de586f0ce9e453a3c9f23074b0f15a3f8f9a1186a",
     "Считайте это радаром, который улавливает фазовые электроны.\n"
     "Он может помочь вам найти то, что вы ищете."),
    ("patch_text01", "message/m160.mbe/000_Sheet1.csv", "m160_050_012", 2,
     "3680f5f05e94dd0b98f3e4eefe6098d58af7d3481dfa1d82985dfd6adb497430",
     "Благодаря этим двум существам долгие годы царили\n"
     "мир и процветание."),
]


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0
    for package, relative, row_id, column, expected_hash, replacement in UPDATES:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        row = matches[0]
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) == expected_hash:
            row[column] = replacement
            changed += 1
            dirty.add(marker)
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")
    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()
