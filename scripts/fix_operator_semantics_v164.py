#!/usr/bin/env python3
"""Polish Operator semantics and register three new runtime M/F variants."""

from __future__ import annotations

from pathlib import Path

from fix_reported_sidequests_v120 import digest, read_document, write_document


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
DATASET = ROOT / "exports/dynamic_gender_confirmed_variants_v066.csv"

UPDATES: list[tuple[str, str, str, int, str, str]] = [
    ("patch_text01", "message/d10.mbe/000_Sheet1.csv", "f_d1003_0020_0010", 2,
     "44f7685706d6c78d6f8515be121e2047435e5b52cc54c4894332098be9f4ec68",
     "Дигивайс позволяет взаимодействовать с такими существами.\n"
     "Одна из его ключевых функций — {fc9ДигиАтака} {r2}."),
    ("patch_text01", "message/field_text.mbe/000_Sheet1.csv", "g_tutorial_1001_0010", 2,
     "b9126fc2ad01d91c13fc841612705f2bc99aa2b8130b17c0c926b7fdabf44721",
     "Похоже, дигимон уже достаточно изучен и готов к конвертации.\n"
     "Попробуй прямо сейчас воспользоваться {fc9Конвертацией}."),
    ("patch_text01", "message/m140.mbe/000_Sheet1.csv", "m140_020_040", 2,
     "443a1e13b6fd6546962bbe93a8af2da3020d04902fbe4728f6d786aaf8b1c2b5",
     "Агент {player}, сейчас самое время собрать\nпобольше информации."),
    ("patch_text01", "message/m180.mbe/000_Sheet1.csv", "m180_110_060", 2,
     "36daf14575ad524d1d30280b7a4f3dc04d591c31c15d0cb20a78eeb2463c0bd1",
     "Там наверняка найдутся зацепки, которые помогут разобраться\n"
     "в происходящем. Продолжай поиски, агент {player}."),
    ("patch_text01", "message/m230.mbe/000_Sheet1.csv", "m230_010_180", 2,
     "b9d1ab6141176c495243b1bb866cdd06efaa3c3de5073d6a01dd35d8b5c8efe8",
     "...твоё задание остаётся прежним: предотвратить Ад Синдзюку.\n"
     "Я всё ещё рассчитываю на тебя, агент {player}!"),
    ("patch_text01", "message/m350.mbe/000_Sheet1.csv", "m350_140_140", 2,
     "4099d08c31fba56233f3f88e1e086e2d20eeee4a1b8293fbfcb27306c0db1aba",
     "Наверное, это всё. Дальше всё зависит от тебя, агент {player}."),
]

DYNAMIC_ROWS = [
    [
        "patch_text01", "message/m070.mbe/000_Sheet1.csv", "m070_100_010",
        "operator",
        "Агент {player}, я попыталась заново оценить текущую ситуацию.",
        "Агент {player}, я попытался заново оценить текущую ситуацию.",
        "1.00", "operator_self_opposite_to_player",
    ],
    [
        "patch_text01", "message/m090.mbe/000_Sheet1.csv", "m090_010_010",
        "operator",
        "Похоже, ты почти не спал, агент {player}?",
        "Похоже, ты почти не спала, агент {player}?",
        "1.00", "operator_addresses_player",
    ],
    [
        "patch_text01", "message/m120.mbe/000_Sheet1.csv", "m120_040_010",
        "operator",
        "Агент {player}... Я только что всё услышала.\n"
        "Ты в Цифровом мире? Я правильно поняла?",
        "Агент {player}... Я только что всё услышал.\n"
        "Ты в Цифровом мире? Я правильно понял?",
        "1.00", "operator_self_opposite_to_player",
    ],
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

    dataset_rows, dataset_encoding, dataset_quote_all = read_document(DATASET)
    header = dataset_rows[0]
    expected_header = [
        "package", "file", "base_id", "role", "male_protagonist_text",
        "female_protagonist_text", "confidence", "basis",
    ]
    if header != expected_header:
        raise SystemExit(f"Unexpected dynamic dataset header: {header!r}")

    added = existing = 0
    by_id = {row[2]: row for row in dataset_rows[1:]}
    for wanted in DYNAMIC_ROWS:
        found = by_id.get(wanted[2])
        if found is None:
            dataset_rows.append(wanted)
            by_id[wanted[2]] = wanted
            added += 1
        elif found == wanted:
            existing += 1
        else:
            raise SystemExit(f"Unexpected dynamic row {wanted[2]}: {found!r}")
    if added:
        dataset_rows = [header, *sorted(dataset_rows[1:], key=lambda row: (row[0], row[1], row[2]))]
        write_document(DATASET, dataset_rows, dataset_encoding, dataset_quote_all)

    print(f"Static targets: {len(UPDATES)}")
    print(f"Static changed: {changed}")
    print(f"Static already current: {current}")
    print(f"Dynamic added: {added}")
    print(f"Dynamic already current: {existing}")


if __name__ == "__main__":
    main()
