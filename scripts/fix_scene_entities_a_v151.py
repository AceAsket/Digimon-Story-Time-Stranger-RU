#!/usr/bin/env python3
"""Canonicalize source-confirmed entity names in the first v141 review batch."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

# package, relative CSV, row id, text column, expected SHA-256, replacement
UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "addcont_03_text01", "message/d350.mbe/000_Sheet1.csv", "d350_020_230", 2,
        "21152347036f24594676b5d83ea6f7c35343436455f535f1b0c225a08f5cd7b6",
        "Куреми... Кодаи Куреми.",
    ),
    (
        "patch_text01", "message/d02.mbe/000_Sheet1.csv", "f_d0201_0390_0010", 2,
        "a2e9cb4b89c5c360a81f7f0258a949db8d9ac7bf5a4bd8c799fd8639bb581d4a",
        "Локомон проходит техническое обслуживание.",
    ),
    (
        "patch_text01", "message/d05.mbe/000_Sheet1.csv", "f_d0506_0080_0090", 2,
        "7452e5d02b07115f8a027cb53e23f30dbe9c7ffba36204ba2276389014f4003b",
        "Найтмон, Серебряная комета!",
    ),
    (
        "patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0603_0100_0010", 2,
        "7cf72face54b87cd7702e5cff4cffef71b5b778dc034cb6b84f8307e93e59826",
        "Витчмон! Сейчас же!",
    ),
    (
        "patch_text01", "message/d09.mbe/000_Sheet1.csv", "f_d0906_0050_0080", 2,
        "fa691b5b5f2c8bc3bd0d38eff9b5d09637e46a8371612d085e86f55ebc0c6944",
        "Вельзевумон...!",
    ),
    (
        "patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "warus_001_4_replay", 2,
        "adc97237226744547c7faa008ef6705d19e23c663d4f5fa5bcb566f8e1abe886",
        "Эй, малыш ВарСидрамон!",
    ),
    (
        "patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "poyo_001_3_replay", 2,
        "30321eaf2a93f1cd89d8420322580f292c03e02202f78af93fe6bce148c63e2c",
        "Поёмон, не так ли?",
    ),
    (
        "patch_text01", "message/m110.mbe/000_Sheet1.csv", "m110_030_010", 2,
        "ce3ccba253d56f507519fef1bd22d84bf694333a1ddee1051b76d013a2a68f06",
        "Хироко!",
    ),
    (
        "patch_text01", "message/m280.mbe/000_Sheet1.csv", "m280_050_020", 2,
        "0282cb3167c6a12fac97b421203d75669a218407cd179edffbffd9af0c2c01a5",
        "Хватит, Ранамон!",
    ),
    (
        "patch_text01", "message/m310.mbe/000_Sheet1.csv", "m310_020_050", 2,
        "f98065b8654b398070c97db1a8bafd792cc980afa417ffba6819689765db549f",
        "Большой Медведь...?{next}",
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
