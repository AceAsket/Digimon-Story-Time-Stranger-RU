#!/usr/bin/env python3
"""Normalize the remaining source-confirmed scene entities to the local glossary."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0302_0900_0010", 2,
     "a9357a3c6fef93ee0481a8db88f1a8206709f09a7f35315006e59f849df701a9",
     "Событие призыва Уэмона"),
    ("patch_text01", "message/d03.mbe/000_Sheet1.csv", "f_d0303_0050_0010", 2,
     "349c91d24bbb42ff746479ad3aac5e3be28967846390108bc52908ab14434064",
     "Ждать Хангёмона здесь?"),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0603_0070_0080", 2,
     "987c9356f7b185e69d20b661026f76ae63a77eb1f77e7562b19190328ab666a8",
     "Дааааа! Оргмон!"),
    ("patch_text01", "message/d06.mbe/000_Sheet1.csv", "f_d0604_0230_0060", 2,
     "0ba268bae35ce7bbcd49d2f6082223045f3273b908b93dd1c438095385fff6c3",
     "В таком случае... Дианамон!"),
    ("patch_text01", "message/d11.mbe/000_Sheet1.csv", "f_d1102_0130_0010", 2,
     "839118b58b5db02389fb33b5f548895dd4be23922acf86507e0933fba6a42c41",
     "Блэк Теилмон! Ты в порядке?!"),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "sylphy_001_2_replay", 2,
     "54c8bbbece3c4286d198097d0c17ce50ee950bb95b217db9f3e50a5952c5168c",
     "Уши Тейлмон."),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "poyo_001_4_replay", 2,
     "d4b891b41a2e9ac4fbea7ed34dc854285e06be92c06856f18d4e60bdc62f3e2a",
     "Я люблю тебя, Поёмон!"),
    ("patch_text01", "message/digimon_chat.mbe/000_Sheet1.csv", "aruda_001_2_replay", 2,
     "a61d712d350db1dec1d1ef2b4048679fe25fb79f86ec817d50f207366c8d1bb8",
     "Агнимон."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "912101035", 2,
     "3d8f89ad9729f84d5ae905f4b9913b0b0b8cf27a1190f59b3faafa0c81738bb5",
     "Сразиться с Той Агумоном."),
    ("patch_text01", "message/m010.mbe/000_Sheet1.csv", "m010_090_081", 2,
     "aac891ffd297ab31756cd03feb53669044ce0c32fb549b9c6eb7fbb96c368087",
     "Пико Девимон."),
    ("patch_text01", "message/m030.mbe/000_Sheet1.csv", "m030_080_025", 2,
     "eefdbb2ee226dba1cb5f52caea656107cac1ff17ade7170926fdd3c53bf2d1a1",
     "...Гомерос."),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_050_050", 2,
     "58d0f5b5e501519a7a00d702497041c82be14f30a94964411b38770816721e3c",
     "Вакхмон?"),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_080_020", 2,
     "caa637051562f83a48d72d5c233f93c934687452d69aed0132de2f87396fc88a",
     "Сиренмон. Что случилось?"),
    ("patch_text01", "message/m200.mbe/000_Sheet1.csv", "m200_020_032", 2,
     "223a2c35bfd65841f2620fba8d3669b1757bd17356b5b0d1eae657e7faa0c643",
     "Теперь я... Эгиохмон."),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0302_0010_0200", 2,
     "f962be06c51f4d868448da36756d4af35d58a8dec2c217154c9a0d1eb84f15fd",
     "Где ВарСидрамон?!"),
    ("patch_text01", "message/rumor_npc.mbe/000_Sheet1.csv", "r_d0501_0010_0010", 2,
     "5e5f8bb7e9130f5947839448e341681123b63285aeeeaa037435c2396ed96491",
     "Все Гардромоны внизу..."),
    ("patch_text01", "message/s070_167.mbe/000_Sheet1.csv", "s070_167_280", 2,
     "fa691b5b5f2c8bc3bd0d38eff9b5d09637e46a8371612d085e86f55ebc0c6944",
     "Вельзевумон...!"),
    ("patch_text01", "message/s110_092.mbe/000_Sheet1.csv", "s110_092_170", 2,
     "7a37c80c0378ed43adb7223a5130950a0e314dc4c5f3ed01937c13b8c59b342b",
     "{next}Краниуммон?"),
    ("patch_text01", "message/s110_112.mbe/000_Sheet1.csv", "s110_112_091", 2,
     "dd94796e5993a72225ab0b5a4ce4c1fe664149a1ad30459fb45bf4cc64dde133",
     "{next}Гэнкумон — твой наставник?"),
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
