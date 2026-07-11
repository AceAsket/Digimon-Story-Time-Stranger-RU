#!/usr/bin/env python3
"""Normalize the next repeated entity group revealed by the scene audit."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/m170.mbe/000_Sheet1.csv", "m170_130_260", 2,
     "ef363700c7f0db0cc13d0968036781cc9edf42b1c41ca434c87552a259011d2e",
     "Хангёмон, вернись!"),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_080_090", 2,
     "b692d98ce1178de3af2501a8ad2de574df9703a3358d57330ab6d4c905cafc58",
     "Вакхмон. Ты... в порядке?"),
    ("patch_text01", "message/m300.mbe/000_Sheet1.csv", "m300_100_230", 2,
     "a5ff62c5d67dab33e656f9b023564f8ddf4b5f2753aa49b43feac7d3c3a1e0d5",
     "Сиренмон умерла?{next}"),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0301_0010_0090", 2,
     "a1ffa9263f7ff57430afc1f691b13b49a06659c782fc2138201d5d895d24e1e3",
     "Где Уэмон?!"),
    ("patch_text01", "message/m260.mbe/000_Sheet1.csv", "m260_110_040", 2,
     "8beefbf750e0df1a4e31b64242ef14149fc0ea3989ab2e65e346ceb603bc0662",
     "Хангёмон?!"),
    ("patch_text01", "message/m290.mbe/000_Sheet1.csv", "m290_060_010", 2,
     "09c2de1a9a69e5a684f5bf9636550aaf7e2023074589741c3da995f7344cfbcb",
     "Вакхмон!"),
    ("patch_text01", "message/m290.mbe/000_Sheet1.csv", "m290_060_280", 2,
     "09c2de1a9a69e5a684f5bf9636550aaf7e2023074589741c3da995f7344cfbcb",
     "Вакхмон!"),
    ("patch_text01", "message/m300.mbe/000_Sheet1.csv", "m300_030_020", 2,
     "40599d8d6e377375dbc6a38f530032fcd76a2fb63011fc75ffff7f008f8ede23",
     "Вакхмон...?"),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0407_0080_0150", 2,
     "4cddb1781eb00d6b50b78838aaebe29d31ea781536af9fe766d4dd919070ef05",
     "Лорд Вакхмон..."),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0407_0090_0100", 2,
     "9edc06355e44241ad4d9b7ca5789ed224d2e78bc5075e466c574cf6a5a3818bb",
     "Это лорд Вакхмон..."),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0407_0090_0310", 2,
     "4cddb1781eb00d6b50b78838aaebe29d31ea781536af9fe766d4dd919070ef05",
     "Лорд Вакхмон..."),
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
