#!/usr/bin/env python3
"""Fix the last confirmed name/calque tails found by the broad audit."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, column, expected SHA-256, replacement
EXACT_UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01",
        "message/s110_093.mbe/000_Sheet1.csv",
        "s110_093_230",
        2,
        "b1c92ad416ee38bf918d3c9c35061a46e722d4b68700ae3fb2cc5a88002cd676",
        "Они бежали в замок, как и планировалось. Теперь Краниуммон\n"
        "сможет присоединиться к битве.",
    ),
]

# package, relative CSV, row id, column, expected SHA-256, old, new, count
TERM_UPDATES: list[tuple[str, str, str, int, str, str, str, int]] = [
    (
        "patch_text01",
        "text/digimon_profile.mbe/000_Sheet1.csv",
        "digimon_0576_profile",
        1,
        "97050c9a4c8eb658066105c5262fbf82ed3103a898d5c3b862823efc0ca2d5ed",
        "Дейтамон",
        "Наномон",
        2,
    ),
]


def main() -> None:
    documents: dict[tuple[str, str], list[list[str]]] = {}
    formats: dict[tuple[str, str], tuple[str, bool]] = {}
    dirty: set[tuple[str, str]] = set()
    changed = current = 0

    def row_for(package: str, relative: str, row_id: str, column: int) -> list[str]:
        marker = (package, relative)
        path = CSV_ROOT / package / relative
        if marker not in documents:
            rows, encoding, quote_all = read_document(path)
            documents[marker] = rows
            formats[marker] = (encoding, quote_all)
        matches = [row for row in documents[marker] if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= column:
            raise SystemExit(f"Missing or ambiguous row {package}:{relative}:{row_id}")
        return matches[0]

    for package, relative, row_id, column, expected_hash, replacement in EXACT_UPDATES:
        row = row_for(package, relative, row_id, column)
        if row[column] == replacement:
            current += 1
        elif digest(row[column]) == expected_hash:
            row[column] = replacement
            changed += 1
            dirty.add((package, relative))
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")

    for package, relative, row_id, column, expected_hash, old, new, count in TERM_UPDATES:
        row = row_for(package, relative, row_id, column)
        if old not in row[column] and row[column].count(new) >= count:
            current += 1
        elif digest(row[column]) == expected_hash and row[column].count(old) == count:
            row[column] = row[column].replace(old, new)
            changed += 1
            dirty.add((package, relative))
        else:
            raise SystemExit(f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}")

    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(CSV_ROOT / package / relative, documents[marker], encoding, quote_all)

    print(f"Targets: {len(EXACT_UPDATES) + len(TERM_UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()
