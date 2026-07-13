#!/usr/bin/env python3
"""Fix source-confirmed address, gender, and register issues around v141 hits."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    (
        "patch_text01", "message/d05.mbe/000_Sheet1.csv",
        "f_d0506_0120_0040", 2,
        "313709319cb91fbbda2b60970df82e87d5ab7317de8043abde011d7d4508275f",
        "Х-хватит! Не отвлекайся, а то проиграешь следующий бой.",
    ),
    (
        "patch_text01", "message/m260.mbe/000_Sheet1.csv",
        "m260_110_170", 2,
        "bc0277f883e3fc458c12266abc0570947bad85f5910cf2f41abf07ede22dca96",
        "Спасибо, я на вас рассчитываю.",
    ),
    (
        "patch_text01", "message/m310.mbe/000_Sheet1.csv",
        "m310_032_030", 2,
        "836a9bf19317c1d1b35ac16f173c0f651de44d838bb5b30d9034e37b65c2a14f",
        "Ну, не тебе же пришлось ждать восемь лет. Восемь лет!\n"
        "Ты вообще представляешь, каково это?",
    ),
    (
        "patch_text01", "message/m320.mbe/000_Sheet1.csv",
        "m320_031_050", 2,
        "0580f3f286df23bf60ee0644619a1df99ad7b3cadceebdf50f405f0fc4fd2ad9",
        "Хех, я шучу. На самом деле я тебе благодарен. Не думал,\n"
        "что ты столько сделаешь ради меня и Старшего Брата!",
    ),
    (
        "patch_text01", "message/s010_180.mbe/000_Sheet1.csv",
        "s010_180_190", 2,
        "06a8463d52fc74463ad67f008d386cd84f59180b71af77919b278be17ae83767",
        "Я помню, как ты звала меня...",
    ),
    (
        "patch_text01", "message/s010_180.mbe/000_Sheet1.csv",
        "s010_180_386", 2,
        "683f8d08e0fa43f6c9a655a02c8cbb72f41980d944b6a66548e84e689b2e03b9",
        "Я... тоже хочу с тобой дружить...",
    ),
    (
        "patch_text01", "message/s010_180.mbe/000_Sheet1.csv",
        "s010_180_390", 2,
        "a5ae0de12b52f83cc302fc40da7fe0d2ba2bc66328e3d3eef80d7e8768340f37",
        "...Спасибо тебе.",
    ),
    (
        "patch_text01", "message/s010_180.mbe/000_Sheet1.csv",
        "s010_180_410", 2,
        "7dbe9d35ad3acb1c8c50b6a5eb2ca0760432cee445dceea350e12f1f9a776bec",
        "С тех пор мы столько раз разговаривали, и ты научила меня\n"
        "стольким словам...",
    ),
    (
        "patch_text01", "message/s020_019.mbe/000_Sheet1.csv",
        "s020_019_640", 2,
        "0c0a71bc6181af54ea6049947877024e8d1d16b2eb682d59474742b35c2c1d7c",
        "Благодаря тебе мы спасли ДжамбоГамемона и нашли\n"
        "жилу хрондигизойта.",
    ),
    (
        "patch_text01", "message/s020_019.mbe/000_Sheet1.csv",
        "s020_019_660", 2,
        "9c2ca490023883e99c7ffcc8b1b65d8aa52722aafd3d773ff5a3ad070eaaa4e2",
        "В любом случае прими этот знак моей признательности.\n"
        "И заходи ко мне в любое время.",
    ),
    (
        "patch_text01", "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_160", 2,
        "808644be3dc8cdd9fede06b1267efc9e17969d227cb31aef4c7a749fe67d0d66",
        "Похоже, сам я домой не вернусь, поэтому ищу того,\n"
        "кто мог бы мне помочь.",
    ),
    (
        "patch_text01", "message/s910_170.mbe/000_Sheet1.csv",
        "s910_170_230", 2,
        "2b159c3499da8dffbafecbe7b8bd8ece5e1f268e5898fc9396699a497f7d1891",
        "Ч-ч-что это за место?! Вы уверены, что это сработает?!",
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
