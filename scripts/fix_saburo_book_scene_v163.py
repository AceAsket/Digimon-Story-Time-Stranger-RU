#!/usr/bin/env python3
"""Repair quotation marks, gender, and literal phrasing in Hiroko's book scene."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "csv/patch_text01/message/s910_169.mbe/000_Sheet1.csv"

UPDATES: list[tuple[str, str, str]] = [
    (
        "s910_169_350",
        "62a37521ffdb87076ba76e9d1bdbb5c7b93c3f9dbf49bf698c7953ab2025693c",
        "«Он не вернулся, поэтому я как староста класса отправилась\n"
        "искать его в учительской».",
    ),
    (
        "s910_169_360",
        "96832431688c6d8830c112f5739cfdc6dda1391fa5f116603272b7a785a7eb39",
        "«Мистер Миура сосредоточенно читал красную книгу.\n"
        "Когда другой учитель заговорил с ним, он сказал:»",
    ),
    (
        "s910_169_370",
        "2c8bcfbe0f40521464b7dfc51c3475cb20da40b0cfc7e4a1d02b28398e0595d0",
        "«Уроки не важны. Я д-должен прочитать эту книгу. Должен!»",
    ),
    (
        "s910_169_380",
        "f8bfa9835352087e22ae10a78e3ac1bfa345b2a1dffb2a907717346fc6b68d96",
        "«Главный герой Сабуро переехал к бабушке.\n"
        "У него не было друзей, поэтому он играл в футбол один».",
    ),
    (
        "s910_169_390",
        "8e3af462a91d484edc50a97289197ea4e10cd4ddfe1aeccd50d236da59d6cb73",
        "«Он играл в футбол так, словно важнее ничего не было.\n"
        "Но в финальном турнире не забил пенальти и бросил футбол».",
    ),
    (
        "s910_169_400",
        "582f3d7072b2dde5a3d7d231b6a98beb5240a66d858984d94ab54246781b33ec",
        "«Потом я сосредоточился на учёбе и получил диплом учителя...\n"
        "...а затем я — нет, Сабуро — стал учителем».",
    ),
    (
        "s910_169_410",
        "9cc16897e17781ee56f0927ad1004dedeb99e377c562008f130505a6b40e8ee8",
        "«Всё совпадает, видите? Это обо мне! И если я не дочитаю\n"
        "до конца, я... я...!»",
    ),
    (
        "s910_169_420",
        "d9e468c11a979acae55a121e177890335556db1a007516e561d8294316d5fe8b",
        "«Затем мистер Миура выбежал из школы с книгой\n"
        "и больше не возвращался».",
    ),
]


def main() -> None:
    rows, encoding, quote_all = read_document(PATH)
    changed = current = 0
    for row_id, expected_hash, replacement in UPDATES:
        matches = [row for row in rows if row and row[0] == row_id]
        if len(matches) != 1 or len(matches[0]) <= 2:
            raise SystemExit(f"Missing or ambiguous row: {row_id}")
        row = matches[0]
        if row[2] == replacement:
            current += 1
        elif digest(row[2]) == expected_hash:
            row[2] = replacement
            changed += 1
        else:
            raise SystemExit(f"Unexpected text {row_id}: {row[2]!r}")
    if changed:
        write_document(PATH, rows, encoding, quote_all)
    print(f"Targets: {len(UPDATES)}")
    print(f"Changed: {changed}")
    print(f"Already current: {current}")


if __name__ == "__main__":
    main()
