#!/usr/bin/env python3
"""Repair the mistranslated pirate idioms in Octmon's survivor scene."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0130_0040", 2,
        "4f0461c330085baa580bf3bc73ce3abd21b3f49c73306a7619c0fd037f391a67",
        "Я-то цел и невредим... но...",
    ),
    (
        "patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0130_0050", 2,
        "8010f0a04d50902e820e85370ed5d16c74eb3c06a39c71b620b8976b325ceb3b",
        "Свора мерзких титанов явилась и разгромила\nнашу славную гавань...",
    ),
    (
        "patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0130_0060", 2,
        "baa3341b6dd528484b01cadf16874f9cf9ad3a7a726353002f67cb96dba94173",
        "Как же всё дошло до такого...?! Ух...",
    ),
    (
        "patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0130_0090", 2,
        "fbff9962b361d7883417e1a2fca46e379c522e828246d390537179de6e796c01",
        "От семьи и друзей ни слуху ни духу...\nНе знаю, что и делать...",
    ),
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
