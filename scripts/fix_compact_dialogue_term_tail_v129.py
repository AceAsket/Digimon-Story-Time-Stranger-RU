#!/usr/bin/env python3
"""Fix the compact-layout tail exposed by Factorial place normalization."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
UPDATES = [
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0090_0010", 2,
     "07e43169d2544ecb9322cb7e9f09f59072f87f29ae3f13dcbfe744ec31b0fe24",
     "*вздох* Здесь так приятно и прохладно — не то что\n"
     "в Факториальной области. Правда, здесь лучше всего?"),
    ("patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0505_0050_0020", 2,
     "010a4ae64680b2519735a423ee749aa79f41e0b2fd5c20a3c87983b2d9f15833",
     "После завершения правого рукава перевозки\nпо Факториальной области стали гораздо эффективнее."),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_010_140", 2,
     "f6e3c242bbe39663dc06f7abe1d52b3a0c9e195208c4a20748a2afc7f0606092",
     "Обычно до храма Юномон добираются по железной дороге Локомона.\n"
     "Но в питающей её Факториальной области возникли проблемы."),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_040_020", 2,
     "8e01175038d488336b98232be1c3432b6622ef50468a0a17245ce3d1f5ac645f",
     "Факториальная область снабжает энергией\nвесь Цифровой мир Илиады!"),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_141", 2,
     "d3e664ac9d19a502ab79f4ed032f578d25e5cfc0bd462143cc64ad8d2801948f",
     "Титаны захватили часть центральной системы управления\n"
     "Факториальной области."),
    ("patch_text01", "message/m150.mbe/000_Sheet1.csv", "m150_070_170", 2,
     "6b89613d8192478b135167991eb7038d2d5b215f64959b4aeb64685dc0505de8",
     "Они захватили часть центральной системы управления\n"
     "Факториального города. Но главная проблема..."),
    ("patch_text01", "text/quest_outline.mbe/000_Sheet1.csv", "78", 1,
     "2ae343a8ff347ea26ae6511483c05a273df4a7ba6e2f04c1bb91ba14d60c664b",
     "БЛИМПМОН ПОТЕРПЕЛ КРУШЕНИЕ В ФАКТОРИАЛЬНОМ ГОРОДЕ\n"
     "И НУЖДАЕТСЯ В РЕМОНТЕ."),
]


def main() -> None:
    documents = {}
    formats = {}
    dirty = set()
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
