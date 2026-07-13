#!/usr/bin/env python3
"""Normalize entity repetitions revealed after the v160 scene pass."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0303_0070_0010", 2,
     "349c91d24bbb42ff746479ad3aac5e3be28967846390108bc52908ab14434064",
     "Ждать Хангёмона здесь?"),
    ("patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0903_0100_0020", 2,
     "f119749be37fcb29d9ed3c3ddbdbc6431b21f445b272c2724857104241a22896",
     "Иди сюда, Уэмон!"),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_060_200", 2,
     "a8db35bb3546b63d9916a02bd228fe0ca9931f3e14f2b2ad9d2e99989f21ea59",
     "Вакхмон вообще слушает?"),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_100_100", 2,
     "40b196d638176367ae87ef76cede88dc64e1fcf425aec3604a206bbbc1e996f6",
     "Эй, Сиренмон."),
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
            raise SystemExit(
                f"Unexpected text {package}:{relative}:{row_id}: {row[column]!r}"
            )
    for marker in sorted(dirty):
        package, relative = marker
        encoding, quote_all = formats[marker]
        write_document(
            CSV_ROOT / package / relative,
            documents[marker],
            encoding,
            quote_all,
        )
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")
    print(f"Files written: {len(dirty)}")


if __name__ == "__main__":
    main()
